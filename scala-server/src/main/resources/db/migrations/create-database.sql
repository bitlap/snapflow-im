-- 一次性建库：具备建库权限的运维账号连接维护库执行，不放在事务中。
-- 创建后重新连接 snapflow-im，再启动初始化；已有部署先核对库名，禁止向空库直接切流。
CREATE DATABASE "snapflow-im";
