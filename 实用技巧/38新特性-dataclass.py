from dataclasses import dataclass, field


@dataclass(order=True, init=True, frozen=True)
class Country:
    name: str
    population: int
    area: float = field(repr=False, compare=False)
    coastline: float = 0

    def beach_per_person(self):
        """每人平均海岸线长度"""
        return (self.coastline * 1000) / self.population


cn = Country('CN', 14, 960.0, 100)
# cn.name = 'cn' #  when frozen is setted , then 'Country' object attribute 'name' is read-only
en = Country('EN', 2, 120.0, 30)
an = Country('AN', 8, 900.0, 600)

print(f"{cn.name=},{cn.population=},{cn.area=},{cn.coastline}")
# print(cn.beach_per_person())

print(sorted((cn, en, an), key=lambda x: x.population, reverse=True))
print(sorted((cn, en, an), key=lambda x: x.area, reverse=True))
print(sorted((cn, en, an), key=lambda x: x.area, reverse=False))
