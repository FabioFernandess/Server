CREATE DATABASE db_fres;

CREATE TABLE fresadora (id SERIAL PRIMARY KEY, nome VARCHAR, valor INT);

CREATE TABLE analise(
   id SERIAL PRIMARY KEY,
   nome_arquivo VARCHAR(255) NOT NULL,
   valor_padrao int,
   status_analise VARCHAR(1) NOT NULL,
    id_fresadora INT,
   CONSTRAINT fk_fresadora
      FOREIGN KEY(id_fresadora) 
	  REFERENCES fresadora(id)
);

create user user_fres with encrypted password 'pass_fres';

grant all privileges on database db_fres to user_fres;