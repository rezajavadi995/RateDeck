from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
import heapq
import re
from ratedeck.market import AssetRegistry, Rate, normalize_text, parse_decimal

@dataclass(frozen=True, slots=True)
class Intent:
    amount: Decimal; source: str; target: str

class IntentParser:
    def __init__(self, registry: AssetRegistry, default_target: str = "irt", max_length: int = 100):
        self.registry, self.default_target, self.max_length = registry, default_target, max_length
    def parse(self, text: str) -> Intent | None:
        text=normalize_text(text)
        if not text or len(text)>self.max_length or text.startswith("/") or "?" in text or "؟" in text: return None
        # A numeric amount is mandatory: this keeps ordinary conversation out.
        match=re.fullmatch(r"\s*([0-9][0-9,.]*)\s*([\w\u0600-\u06ff]+)(?:\s*(?:به|to)\s*([\w\u0600-\u06ff]+))?\s*",text)
        if not match: return None
        try:
            source=self.registry.resolve(match.group(2)).key
            target=self.registry.resolve(match.group(3)).key if match.group(3) else self.default_target
            return Intent(parse_decimal(match.group(1)),source,target)
        except ValueError: return None

@dataclass(frozen=True, slots=True)
class Conversion:
    amount: Decimal; source: str; target: str; path: tuple[Rate,...]
    @property
    def provenance(self): return tuple(item for edge in self.path for item in edge.provenance)
    @property
    def oldest_timestamp(self): return min(edge.timestamp for edge in self.path)

class ConversionGraph:
    def __init__(self, rates: list[Rate]):
        self.edges: dict[str,list[Rate]]={}
        for rate in rates:
            self.edges.setdefault(rate.source,[]).append(rate)
            if rate.value: self.edges.setdefault(rate.target,[]).append(Rate(rate.target,rate.source,Decimal(1)/rate.value,rate.provider,rate.timestamp,rate.provenance+("inverse",)))
    def convert(self, amount: Decimal, source: str, target: str, max_hops: int = 3) -> Conversion:
        queue=[(0,source,amount,())]; visited={}
        while queue:
            hops,node,value,path=heapq.heappop(queue)
            if node==target: return Conversion(value,source,target,path)
            if hops>=max_hops or visited.get(node,99)<=hops: continue
            visited[node]=hops
            for edge in sorted(self.edges.get(node,[]),key=lambda e:(e.provider,e.target)):
                heapq.heappush(queue,(hops+1,edge.target,value*edge.value,path+(edge,)))
        raise ValueError("no conversion route")

class StarsPackages:
    def __init__(self): self.packages: dict[Decimal,Decimal]={}
    def set_line(self,line: str) -> tuple[Decimal,Decimal]:
        parts=normalize_text(line).split()
        if len(parts)!=2: raise ValueError("expected: quantity price")
        quantity,price=map(parse_decimal,parts)
        if quantity<=0 or price<=0 or quantity != quantity.to_integral(): raise ValueError("positive integral quantity required")
        self.packages[quantity]=price; return quantity,price
    def price(self,quantity: Decimal) -> Decimal:
        if quantity not in self.packages: raise ValueError("exact Stars package is not configured")
        return self.packages[quantity]
