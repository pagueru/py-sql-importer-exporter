-- 1. Criar a database
CREATE DATABASE DB_CLIENTES;

-- 2. Usar a database
USE DB_CLIENTES;

-- 3. Criar a tabela CLIENTES
CREATE TABLE CLIENTES (
    ID_CLIENTE INT PRIMARY KEY,
    NOME NVARCHAR(100),
    EMAIL NVARCHAR(100)
);

-- 4. Inserir 10 registros fake
INSERT INTO CLIENTES (ID_CLIENTE, NOME, EMAIL) VALUES
(1, 'Ana Souza', 'ana.souza@email.com'),
(2, 'Bruno Lima', 'bruno.lima@email.com'),
(3, 'Carla Mendes', 'carla.mendes@email.com'),
(4, 'Daniel Rocha', 'daniel.rocha@email.com'),
(5, 'Eduarda Silva', 'eduarda.silva@email.com'),
(6, 'Felipe Costa', 'felipe.costa@email.com'),
(7, 'Gabriela Dias', 'gabriela.dias@email.com'),
(8, 'Henrique Alves', 'henrique.alves@email.com'),
(9, 'Isabela Martins', 'isabela.martins@email.com'),
(10, 'João Pereira', 'joao.pereira@email.com');
