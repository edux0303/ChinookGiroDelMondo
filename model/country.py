from dataclasses import dataclass, field


@dataclass
class Country:
    nome: str
    ricavo: float
    clienti: set = field(default_factory=set)
    artisti: set = field(default_factory=set)

    def __hash__(self):
        return hash(self.nome)

    def __eq__(self, other):
        return self.nome == other.nome

    def __str__(self):
        return self.nome