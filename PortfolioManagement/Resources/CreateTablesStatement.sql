create table transaction
(
    isin               varchar,
    wkn                varchar,
    amountofbonds      double precision not null,
    transactiondate    date             not null,
    typeoftransaction  varchar          not null,
    transactioncomment varchar,
    price              double precision not null,
    depot              varchar,
    currency           varchar,
    exchange           varchar,
    "transactionID"    serial
        constraint transaction_pk
            primary key
);

alter table transaction
    owner to root;

create table "PDFs"
(
    pdfid    serial
        constraint pdfs_pk
            primary key,
    date     date    not null,
    type     varchar,
    comment  varchar,
    filepath varchar not null
);

alter table "PDFs"
    owner to root;

create table "Bond"
(
    "BondID"  serial
        constraint bond_pk
            primary key,
    isin      varchar,
    wkn       varchar,
    "Comment" varchar,
    "Name"    varchar
);

alter table "Bond"
    owner to root;

create table "AssociatedFiles"
(
    "AssociatedFilesID" serial
        constraint associatedfiles_pk
            primary key,
    "FKBondId"          integer
        constraint "FK_Bond"
            references "Bond",
    fkpdfid             integer
        constraint fk_pdf
            references "PDFs"
            on update set null on delete set null,
    "FKTransactionID"   integer
        constraint "FK_Transaction"
            references transaction
);

alter table "AssociatedFiles"
    owner to root;

create table "Price"
(
    isin        varchar,
    price       double precision,
    "priceDate" date
);

alter table "Price"
    owner to root;
