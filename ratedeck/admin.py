from __future__ import annotations
from dataclasses import dataclass
from ratedeck.telegram import Callback

@dataclass(frozen=True,slots=True)
class AdminSection:
    key:str; title_fa:str; description_fa:str

SECTIONS={s.key:s for s in (
 AdminSection("providers","منابع و API","حالت، کلید، سلامت و مسیرها"), AdminSection("assets","دارایی‌ها","جستجو، علاقه‌مندی، نام مستعار و نگاشت"),
 AdminSection("content","متن‌ها و جای‌نگهدارها","فرمان‌ها، کپشن و فیلدها"), AdminSection("buttons","دکمه‌ها","برچسب، سبک، آیکن و چیدمان مجاز"),
 AdminSection("stars","بسته‌های استارز","قیمت دقیق بسته‌ها"), AdminSection("diagnostics","عیب‌یابی","بررسی محلی و آزمون زنده محدود"),
 AdminSection("audit","گزارش و ممیزی","رویدادهای امن و سلامت سیستم"),
)}

class AdminScreens:
    def root(self)->str: return "پنل مدیریت RateDeck\n"+"\n".join(f"• {s.title_fa}" for s in SECTIONS.values())
    def render(self,callback:Callback)->str:
        section=SECTIONS.get(callback.action)
        if not section: raise ValueError("unknown admin action")
        return f"{section.title_fa}\n{section.description_fa}"
