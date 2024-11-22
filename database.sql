CREATE DATABASE db_fres;

CREATE TABLE fresadora (id SERIAL PRIMARY KEY, nome VARCHAR not null, valor INT not null);

CREATE TABLE analise(
   id SERIAL PRIMARY KEY,
   nome_arquivo VARCHAR(255) NOT NULL,
   valor_padrao int NOT null,
   status_analise VARCHAR(1) NOT NULL,
   data_analise timestamp NOT NULL,
    id_fresadora INT NOT null,
   CONSTRAINT fk_fresadora
      FOREIGN KEY(id_fresadora) 
	  REFERENCES fresadora(id)
);

ALTER TABLE analise ALTER COLUMN data_analise SET DEFAULT now();

ALTER TABLE fresadora ADD COLUMN variavel varchar;