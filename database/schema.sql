CREATE DATABASE IF NOT EXISTS db_esteticando;

USE db_esteticando;

CREATE TABLE IF NOT EXISTS tb_cliente (
  cli_id INT AUTO_INCREMENT PRIMARY KEY,
  cli_dataCriacao DATE NOT NULL,
  cli_nome VARCHAR(100) NOT NULL,
  cli_email VARCHAR(100) NOT NULL,
  cli_senha VARCHAR(255) NOT NULL,
  cli_cpf CHAR(11) NOT NULL,
  cli_telefone VARCHAR(15) NOT NULL,
  cli_endereco VARCHAR(255) DEFAULT ''
);

CREATE TABLE IF NOT EXISTS tb_categoria (
  cat_id INT AUTO_INCREMENT PRIMARY KEY,
  cat_nome VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS tb_estabelecimento (
  est_id INT AUTO_INCREMENT PRIMARY KEY,
  est_dataCriacao DATE NOT NULL,
  est_nome VARCHAR(100) NOT NULL,
  est_descricao VARCHAR(45) NOT NULL,
  est_cnpj CHAR(14) NOT NULL,
  est_email VARCHAR(100) NOT NULL,
  est_telefone VARCHAR(15) NOT NULL,
  est_cat_id INT NOT NULL,
  FOREIGN KEY (est_cat_id) REFERENCES tb_categoria (cat_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tb_endereco_estabelecimento (
  end_id INT AUTO_INCREMENT PRIMARY KEY,
  end_numero VARCHAR(10) NOT NULL,
  end_complemento VARCHAR(100),
  end_bairro VARCHAR(100) NOT NULL,
  end_rua VARCHAR(45) NOT NULL,
  end_cidade VARCHAR(100) NOT NULL,
  end_estado CHAR(2) NOT NULL,
  end_cep CHAR(8) NOT NULL,
  end_est_id INT NOT NULL,
  FOREIGN KEY (end_est_id) REFERENCES tb_estabelecimento(est_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tb_profissional (
  pro_id INT AUTO_INCREMENT PRIMARY KEY,
  pro_dataCriacao DATE NOT NULL,
  pro_nome VARCHAR(100) NOT NULL,
  pro_email VARCHAR(100) NOT NULL,
  pro_senha VARCHAR(255) NOT NULL,
  pro_cpf CHAR(11) NOT NULL,
  pro_telefone VARCHAR(15) NOT NULL,
  pro_est_id INT DEFAULT NULL,
  pro_cat_id INT DEFAULT NULL,
  FOREIGN KEY (pro_est_id) REFERENCES tb_estabelecimento(est_id) ON DELETE CASCADE,
  FOREIGN KEY (pro_cat_id) REFERENCES tb_categoria(cat_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tb_servico (
  ser_id INT AUTO_INCREMENT PRIMARY KEY,
  ser_dataCriacao DATE NOT NULL,
  ser_nome VARCHAR(100) NOT NULL,
  ser_preco FLOAT NOT NULL,
  ser_duracao INT NOT NULL,
  ser_descricao TEXT,
  ser_cat_id INT NOT NULL,
  ser_est_id INT NOT NULL,
  FOREIGN KEY (ser_est_id) REFERENCES tb_estabelecimento(est_id) ON DELETE CASCADE,
  FOREIGN KEY (ser_cat_id) REFERENCES tb_categoria(cat_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tb_disponibilidade_estabelecimento (
  des_id INT AUTO_INCREMENT PRIMARY KEY,
  des_est_id INT NOT NULL,
  des_dia ENUM("segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sabado", "domingo") NOT NULL,
  des_horarioInicio TIME NOT NULL,
  des_horarioFim TIME NOT NULL,
  FOREIGN KEY (des_est_id) REFERENCES tb_estabelecimento(est_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tb_disponibilidade_profissional (
  dip_id INT AUTO_INCREMENT PRIMARY KEY,
  dip_pro_id INT NOT NULL,
  dip_dia ENUM("segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sabado", "domingo") NOT NULL,
  dip_horarioInicio TIME NOT NULL,
  dip_horarioFim TIME NOT NULL,
  FOREIGN KEY (dip_pro_id) REFERENCES tb_profissional(pro_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tb_agendamento (
  age_id INT AUTO_INCREMENT PRIMARY KEY,
  age_dataCriacao DATETIME NOT NULL,
  age_horario TIME NOT NULL,
  age_valorTotal FLOAT NOT NULL,
  age_quantidade INT NOT NULL,
  age_duracao INT NOT NULL,
  age_status ENUM('Agendado', 'Cancelado', 'Concluído') NOT NULL,
  age_cli_id INT NOT NULL,
  age_ser_id INT NOT NULL,
  age_pro_id INT NOT NULL,
  FOREIGN KEY (age_cli_id) REFERENCES tb_cliente(cli_id) ON DELETE CASCADE,
  FOREIGN KEY (age_ser_id) REFERENCES tb_servico(ser_id) ON DELETE CASCADE,
  FOREIGN KEY (age_pro_id) REFERENCES tb_profissional(pro_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tb_avaliacao (
  ava_id INT AUTO_INCREMENT PRIMARY KEY,
  ava_dataCriacao DATE NOT NULL,
  ava_nota VARCHAR(45) NOT NULL, 
  ava_comentario TEXT,
  ava_cli_id INT NOT NULL,
  ava_age_id INT NOT NULL,
  FOREIGN KEY (ava_cli_id) REFERENCES tb_cliente(cli_id) ON DELETE CASCADE,
  FOREIGN KEY (ava_age_id) REFERENCES tb_agendamento(age_id) ON DELETE CASCADE
);




