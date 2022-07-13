import datetime as dt

from marshmallow import Schema, fields


class Fresadora():
  def __init__(self, nome, valor, type):
    self.nome = nome
    self.valor = valor
    self.dataCriacao = dt.datetime.now()

  def __repr__(self):
    return '<Fresadora(name={self.nome!r})>'.format(self=self)


class FresadoraSchema(Schema):
  nome = fields.Str()
  valor = fields.Number()
  dataCriacao = fields.Date()