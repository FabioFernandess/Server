CREATE DATABASE db_fres;

CREATE TABLE fresadora (id SERIAL PRIMARY KEY, nome VARCHAR, valor INT);

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

