-- 写入表 snap_flow.im_schema：IM 初始化完成标记。
-- 写入字段 snap_flow.im_schema.version：协议或模板版本。
-- v1 / DML：与 DDL/v1.sql 同 PR 同步维护。
-- snap_flow.im_schema：当前结构初始化完成标记；version=1，不是升级链版本。
INSERT INTO snap_flow.im_schema(version) VALUES(1);
