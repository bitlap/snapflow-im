"""检查普通 DDL/DML、源码注释、一次性脚本边界和同 PR 版本配对。"""

import json
import os
import re
import subprocess
from pathlib import Path


def statements(s):
    out = []
    start = i = 0
    quote = None
    dollar = None
    block = 0
    line = False
    while i < len(s):
        c = s[i]
        n = s[i : i + 2]
        if line:
            if c == "\n":
                line = False
        elif block:
            if n == "/*":
                block += 1
                i += 1
            elif n == "*/":
                block -= 1
                i += 1
        elif dollar:
            if s.startswith(dollar, i):
                i += len(dollar) - 1
                dollar = None
        elif quote:
            if c == quote:
                if i + 1 < len(s) and s[i + 1] == quote:
                    i += 1
                else:
                    quote = None
        elif n == "--":
            line = True
            i += 1
        elif n == "/*":
            block = 1
            i += 1
        elif c in "'\"`":
            quote = c
        elif c == "$" and (m := re.match(r"\$(?:[A-Za-z_]\w*)?\$", s[i:])):
            dollar = m[0]
            i += len(dollar) - 1
        elif c == ";":
            out.append(s[start : i + 1])
            start = i + 1
        i += 1
    if s[start:].strip():
        out.append(s[start:])
    return out


def code(s):
    return re.sub(r"--[^\n]*|/\*.*?\*/", "", s, flags=re.DOTALL).strip()


def mask(s):
    out = list(s)
    i = 0
    while i < len(s):
        if s.startswith("--", i):
            j = s.find("\n", i)
            j = len(s) if j < 0 else j
        elif s.startswith("/*", i):
            j = s.find("*/", i + 2)
            j = len(s) if j < 0 else j + 2
        elif s[i] in "'\"`":
            q = s[i]
            j = i + 1
            while j < len(s):
                if s[j] == q:
                    if j + 1 < len(s) and s[j + 1] == q:
                        j += 2
                        continue
                    j += 1
                    break
                j += 1
        else:
            i += 1
            continue
        for k in range(i, j):
            if out[k] != "\n":
                out[k] = " "
        i = j
    return "".join(out)


create = re.compile(
    r"CREATE\s+(?:EXTERNAL\s+)?TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([\w.${}]+)\s*\(",
    re.IGNORECASE,
)


def tables(s):
    for m in create.finditer(s):
        start = m.end()
        depth = 1
        i = start
        masked = mask(s[start:])
        while i < len(s) and depth:
            c = masked[i - start]
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
            i += 1
        yield m, m[1], start, i - 1


def fields(body):
    masked = mask(body)
    depth = 0
    start = 0
    for i, c in enumerate(masked):
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        elif c == "," and depth == 0:
            yield body[start:i]
            start = i + 1
    yield body[start:]


def check(root):
    """只读取当前检出与 git 差异；不连接数据库，不执行 SQL。"""
    root = Path(root)
    names = set(
        subprocess.check_output(
            ["git", "ls-files", "-co", "--exclude-standard"], cwd=root, text=True
        ).splitlines()
    )
    changed = set(
        subprocess.check_output(
            ["git", "diff", "--name-only", "HEAD"], cwd=root, text=True
        ).splitlines()
    )
    changed.update(
        subprocess.check_output(
            ["git", "ls-files", "--others", "--exclude-standard"], cwd=root, text=True
        ).splitlines()
    )
    # 在 PR CI 中比较整个 PR，而非仅比较干净 checkout 的工作区。
    base_revision = os.environ.get("SQL_POLICY_BASE")
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not base_revision and event_path and Path(event_path).is_file():
        event = json.loads(Path(event_path).read_text())
        base_revision = event.get("pull_request", {}).get("base", {}).get("sha")
    if base_revision:
        changed.update(
            subprocess.check_output(
                ["git", "diff", "--name-only", base_revision], cwd=root, text=True
            ).splitlines()
        )
    errors = []
    forbidden = re.compile(
        r"\bCREATE\s+(?:OR\s+REPLACE\s+)?(?:(?:CONSTRAINT|EVENT)\s+)?(?:FUNCTION|TRIGGER|PROCEDURE)\b|\bCALL\s+\w|\bDO\s+\$",
        re.IGNORECASE,
    )
    for name in sorted(names):
        path = root / name
        if not path.is_file():
            continue
        if path.suffix == ".sql":
            source = path.read_text()
            plain = mask(source)
            once = "migrations" in path.parts
            fixture = name.startswith("src/test/resources/migrations/legacy-triggers/")
            if not once and re.search(r"(?m)^\s*\\", plain):
                errors.append(
                    f"{name}: 普通 SQL 禁止隐式换库或 psql 命令；一次性脚本单独存放"
                )
            if re.search(r"\bCOMMENT\s+(?:ON|\')", plain, re.IGNORECASE):
                errors.append(
                    f"{name}: 用 -- 或 /* */ 源码注释，禁止 COMMENT 元数据语句"
                )
            if forbidden.search(plain) and not once:
                errors.append(f"{name}: 函数、触发器、过程及 DO/CALL 仅允许一次性迁移")
            if once and not fixture:
                # 一次性 helper 必须同脚本显式清理，不能留下持续运行的数据库业务代码。
                for match in re.finditer(
                    r"CREATE\s+(?:OR\s+REPLACE\s+)?(?:(?:CONSTRAINT|EVENT)\s+)?(FUNCTION|TRIGGER|PROCEDURE)\s+([\w.]+)",
                    plain,
                    re.IGNORECASE,
                ):
                    if not re.search(
                        r"DROP\s+"
                        + match[1]
                        + r"\s+(?:IF EXISTS\s+)?"
                        + re.escape(match[2])
                        + r"\b",
                        plain[match.end() :],
                        re.IGNORECASE,
                    ):
                        errors.append(
                            f"{name}: 一次性自定义对象 {match[2]} 缺少脚本内 DROP"
                        )
            for match, table, start, end in tables(source):
                prefix = source[max(0, match.start() - 1200) : match.start()]
                if not re.search(r"--[^\n]*[^\s-]|/\*", prefix):
                    errors.append(f"{name}: 表 {table} 缺少源码说明")
                body = source[start:end]
                # Handwritten definitions put each column on a separate annotated line.
                column_lines = list(
                    re.finditer(
                        r'(?m)^\s*[`"]?(\w+)[`"]?\s+(?:BIGSERIAL|SERIAL|BIGINT|INTEGER|INT|SMALLINT|TEXT|VARCHAR|CHAR|BOOLEAN|TIMESTAMPTZ|TIMESTAMP|DATE|JSONB|JSON|HSTORE|STRING|DOUBLE|FLOAT|DECIMAL|NUMERIC)\b',
                        body,
                        re.IGNORECASE,
                    )
                )
                for index, column in enumerate(column_lines):
                    stop = (
                        column_lines[index + 1].start()
                        if index + 1 < len(column_lines)
                        else len(body)
                    )
                    if not re.search(r"--\s*\S|/\*\s*\S", body[column.start() : stop]):
                        errors.append(f"{name}: 字段 {table}.{column[1]} 缺少源码说明")
            for statement in statements(source):
                sql = code(statement)
                if re.match(r"ALTER\s+TABLE", sql, re.IGNORECASE):
                    for column in re.findall(
                        r"ADD\s+(?:COLUMN\s+)?(?:IF NOT EXISTS\s+)?(\w+)\s+(?:VARCHAR|TEXT|JSONB|SMALLINT|INTEGER|BIGINT|BIGSERIAL|SERIAL|TIMESTAMPTZ|BOOLEAN|DATE|TIMESTAMP|HSTORE)",
                        sql,
                        re.IGNORECASE,
                    ):
                        position = source.find(statement)
                        context = source[
                            max(0, position - 1500) : position + len(statement)
                        ]
                        if not re.search(
                            r"--[^\n]*\b"
                            + re.escape(column)
                            + r"\b|/\*[^*]*\b"
                            + re.escape(column)
                            + r"\b",
                            context,
                        ):
                            errors.append(f"{name}: 新增字段 {column} 缺少源码说明")
            if "/DDL/" in name:
                for statement in statements(source):
                    if re.match(
                        r"(INSERT|UPDATE|DELETE|MERGE)\b",
                        code(statement),
                        re.IGNORECASE,
                    ):
                        errors.append(f"{name}: 数据写入应移至同版本 DML")
            if "/DML/" in name:
                for statement in statements(source):
                    if re.match(
                        r"(CREATE|ALTER|DROP|TRUNCATE)\b",
                        code(statement),
                        re.IGNORECASE,
                    ):
                        errors.append(f"{name}: 结构变更应移至同版本 DDL")
        elif (
            name.startswith(("src/main/", "app/", "scala-server/src/main/"))
            and path.suffix in {".scala", ".py", ".java"}
            and re.search(
                r"\bCREATE\s+(?:OR\s+REPLACE\s+)?(?:(?:CONSTRAINT|EVENT)\s+)?(?:FUNCTION|TRIGGER|PROCEDURE)\s+\w",
                path.read_text(),
                re.IGNORECASE,
            )
        ):
            errors.append(f"{name}: 运行代码禁止安装数据库函数、触发器或过程")
    for base in [
        "src/main/resources/version-sqls",
        "scala-server/src/main/resources/db",
        "sql",
        "sqls",
    ]:
        ddl, dml = root / base / "DDL", root / base / "DML"
        if not ddl.is_dir():
            continue
        left, right = (
            {p.name for p in ddl.glob("*.sql")},
            {p.name for p in dml.glob("*.sql")},
        )
        for version in left ^ right:
            errors.append(
                f"{base}/{version}: DDL/DML 版本必须成对，空变更也保留说明文件"
            )
        for version in left & right:
            pair = {f"{base}/DDL/{version}", f"{base}/DML/{version}"}
            migration = f"{base}/migrations/{version}"
            if (pair | {migration}) & changed and not pair <= changed:
                errors.append(f"{base}/{version}: 同 PR 必须同步更新 DDL 与 DML")
    if errors:
        raise SystemExit("\n".join(errors))
    print(
        "SQL policy passed: ordinary DDL/DML, source comments, one-use scripts, paired PR versions"
    )
