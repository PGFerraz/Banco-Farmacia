from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Boolean, Date, ForeignKey
)
from sqlalchemy.orm import relationship, declarative_base, sessionmaker
from datetime import date

Base = declarative_base()

class Endereco(Base):
    __tablename__ = 'endereco'
    id = Column(Integer, primary_key=True, autoincrement=True)
    logradouro = Column(String(100))
    bairro = Column(String(100))
    cep = Column(String(15))

    cliente = relationship("Cliente", back_populates="endereco", uselist=False)


class Cliente(Base):
    __tablename__ = 'cliente'
    cpf = Column(String(14), primary_key=True)
    nome = Column(String(100))
    telefone = Column(String(20))
    endereco_id = Column(Integer, ForeignKey('endereco.id'))

    endereco = relationship("Endereco", back_populates="cliente")
    vendas = relationship("Venda", back_populates="cliente")


class Produto(Base):
    __tablename__ = 'produto'
    id_produto = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100))
    preco = Column(Float)
    qtd_estoque = Column(Integer)
    precisa_receita = Column(Boolean, default=False)

    vendas = relationship("VendaProduto", back_populates="produto")


class Receita(Base):
    __tablename__ = 'receita'
    id_receita = Column(Integer, primary_key=True, autoincrement=True)
    nome_medico = Column(String(100))
    crm_medico = Column(String(20))
    data_emissao = Column(Date)
    validade = Column(Date)

    vendas = relationship("Venda", back_populates="receita")


class Venda(Base):
    __tablename__ = 'venda'
    id_venda = Column(Integer, primary_key=True, autoincrement=True)
    data_venda = Column(Date)
    valor = Column(Float)
    cpf_cliente = Column(String(14), ForeignKey('cliente.cpf'))
    receita_id = Column(Integer, ForeignKey('receita.id_receita'), nullable=True)

    cliente = relationship("Cliente", back_populates="vendas")
    receita = relationship("Receita", back_populates="vendas")
    produtos = relationship("VendaProduto", back_populates="venda")


class VendaProduto(Base):
    __tablename__ = 'venda_produto'
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_venda = Column(Integer, ForeignKey('venda.id_venda'))
    id_produto = Column(Integer, ForeignKey('produto.id_produto'))
    quantidade = Column(Integer, default=1)

    venda = relationship("Venda", back_populates="produtos")
    produto = relationship("Produto", back_populates="vendas")
