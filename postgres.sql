-- DB作成
CREATE DATABASE rakuten;


-- テーブル作成
CREATE TABLE shisan (
    id                  serial,
    datetime            timestamp without time zone,
    shisan              varchar(80),
    jikahyoukagaku      int,
    zenjitsuhi          int,
    zenjitsuhi_p        float,
    zengetsuhi          int,
    zengetsuhi_p        float,
    hyoukasoneki        int,
    hyoukasoneki_p      float,
    primary key(id)
);

CREATE TABLE ginkou (
    id                  serial,
    datetime            timestamp without time zone,
    zandaka             int,
    primary key(id)
);

CREATE TABLE syouhin (
    id                  serial,
    datetime            timestamp without time zone,
    syubetsu            varchar(20),
    code                varchar(10),
    meigara             varchar(80),
    kouza               varchar(20),
    hoyusu              int,
    hoyusu_tanni        varchar(10),
    heikinsyutokukagaku float,
    heikinsyutokukagaku_tanni varchar(10),
    genzaiti            float,
    genzaiti_tanni      varchar(10),
    genzaiti_koushin    varchar(30),
    sankou_kawase       varchar(20),
    zenjitsuhi          float,
    zenjitsuhi_tanni    varchar(10),
    jikahyoukagaku      float,
    jikahyoukagaku_gaika    float,
    hyoukasoneki        float,
    hyoukasoneki_p      float,
    primary key(id)
);

CREATE TABLE kawase (
    id                  serial,
    datetime            timestamp without time zone,
    tsuuka              varchar(20),
    rate                float,
    rate_tanni          varchar(20),
    koushin_time        varchar(30),
    primary key(id)
);

-- テーブル削除
DROP TABLE shisan;
DROP TABLE ginkou;
DROP TABLE syouhin;
DROP TABLE kawase;

--SQL参考
select * from ginkou where datetime='2021/04/24 10:29:53';
delete from ginkou where datetime='2021/04/24 10:29:53';

select * from shisan where shisan='米国株式' order by datetime desc;

