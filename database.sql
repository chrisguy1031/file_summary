CREATE TABLE file_summary (
    file_id VARCHAR2(36)  NOT NULL PRIMARY KEY,
    app_id  NUMBER(4, 0)  NOT NULL,
    app_user    VARCHAR2(100) NOT NULL,
    upload_date DATE  DEFAULT SYSDATE,
    file_name   VARCHAR2(200) NOT NULL,
    file_ext    VARCHAR2(10),
    file_size   NUMBER(10, 0),
    file_path   VARCHAR2(500),
    batch   VARCHAR2(100),
    file_seq    NUMBER(5, 0)  NOT NULL,
    language    VARCHAR2(50),
    status  NUMBER(2, 0),
    summary_en  CLOB,
    summary_cn  CLOB,
    summary_kr  CLOB,
    summary_ja  CLOB
);