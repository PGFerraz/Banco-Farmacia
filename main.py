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

engine = create_engine("sqlite:///farmacia.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def adicionar_cliente():
    cpf = input("CPF: ")
    nome = input("Nome: ")
    telefone = input("Telefone: ")
    logradouro = input("Logradouro: ")
    bairro = input("Bairro: ")
    cep = input("CEP: ")

    endereco = Endereco(logradouro=logradouro, bairro=bairro, cep=cep)
    cliente = Cliente(cpf=cpf, nome=nome, telefone=telefone, endereco=endereco)
    session.add(cliente)
    session.commit()
    print("Cliente adicionado com sucesso!\n")


def listar_clientes():
    clientes = session.query(Cliente).all()
    for c in clientes:
        print(f"CPF: {c.cpf} | Nome: {c.nome} | Telefone: {c.telefone} | Endereço: {c.endereco.logradouro}, {c.endereco.bairro} - {c.endereco.cep}")
    if not clientes:
        print("Nenhum cliente cadastrado.\n")


def deletar_cliente():
    cpf = input("Informe o CPF do cliente a deletar: ")
    cliente = session.query(Cliente).filter_by(cpf=cpf).first()
    if cliente:
        session.delete(cliente)
        session.commit()
        print("Cliente deletado.\n")
    else:
        print("Cliente não encontrado.\n")


def adicionar_produto():
    nome = input("Nome do produto: ")
    preco = float(input("Preço: "))
    qtd = int(input("Quantidade em estoque: "))
    precisa = input("Precisa de receita? (s/n): ").lower() == 's'
    produto = Produto(nome=nome, preco=preco, qtd_estoque=qtd, precisa_receita=precisa)
    session.add(produto)
    session.commit()
    print("Produto adicionado!\n")


def listar_produtos():
    produtos = session.query(Produto).all()
    for p in produtos:
        receita = "Sim" if p.precisa_receita else "Não"
        print(f"ID: {p.id_produto} | Nome: {p.nome} | Preço: R${p.preco:.2f} | Estoque: {p.qtd_estoque} | Receita: {receita}")
    if not produtos:
        print("Nenhum produto cadastrado.\n")


def deletar_produto():
    idp = int(input("Informe o ID do produto: "))
    produto = session.query(Produto).filter_by(id_produto=idp).first()
    if produto:
        session.delete(produto)
        session.commit()
        print("Produto deletado.\n")
    else:
        print("Produto não encontrado.\n")


def adicionar_venda():
    cpf = input("CPF do cliente: ")
    cliente = session.query(Cliente).filter_by(cpf=cpf).first()
    if not cliente:
        print("Cliente não encontrado.\n")
        return

    valor_total = 0
    itens = []

    while True:
        listar_produtos()
        idp = input("Digite o ID do produto (ou Enter para finalizar): ")
        if not idp:
            break
        idp = int(idp)
        produto = session.query(Produto).filter_by(id_produto=idp).first()
        if not produto:
            print("Produto não encontrado.")
            continue
        qtd = int(input("Quantidade: "))
        if produto.qtd_estoque < qtd:
            print("Estoque insuficiente!")
            continue
        valor_total += produto.preco * qtd
        produto.qtd_estoque -= qtd
        itens.append((produto, qtd))

    venda = Venda(data_venda=date.today(), valor=valor_total, cliente=cliente)
    session.add(venda)
    session.commit()

    for produto, qtd in itens:
        vp = VendaProduto(venda=venda, produto=produto, quantidade=qtd)
        session.add(vp)
    session.commit()

    print(f"Venda registrada! Valor total: R${valor_total:.2f}\n")


def listar_vendas():
    vendas = session.query(Venda).all()
    for v in vendas:
        print(f"ID: {v.id_venda} | Cliente: {v.cliente.nome} | Data: {v.data_venda} | Valor: R${v.valor:.2f}")
    if not vendas:
        print("Nenhuma venda registrada.\n")

def menu():
    while True:
        print("""
======== MENU FARMÁCIA ========
1. Adicionar Cliente
2. Listar Clientes
3. Deletar Cliente
4. Adicionar Produto
5. Listar Produtos
6. Deletar Produto
7. Registrar Venda
8. Listar Vendas
0. Sair
""")
        opc = input("Escolha: ")
        if opc == "1":
            adicionar_cliente()
        elif opc == "2":
            listar_clientes()
        elif opc == "3":
            deletar_cliente()
        elif opc == "4":
            adicionar_produto()
        elif opc == "5":
            listar_produtos()
        elif opc == "6":
            deletar_produto()
        elif opc == "7":
            adicionar_venda()
        elif opc == "8":
            listar_vendas()
        elif opc == "0":
            print("Saindo...")
            break
        else:
            print("Opção inválida!\n")


if __name__ == "__main__":
    menu()

