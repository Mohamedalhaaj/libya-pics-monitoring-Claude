"""25-28 June 2026 PICS report, authored by Claude (editor) from the complete
scrape (date-archive fix). Each bullet matches rows by distinctive title
substrings, so attribution is pulled from the data and survives re-scrapes.
"""
import csv, re
from utils.models import HeadlineSource, ReportHeadline, ReportSection, ReportSubsection, StructuredReport
from utils.outlets import canonicalize_outlet
from utils.exports import write_word_report

ROWS = list(csv.DictReader(open('data/2026-06-25_28/libya_media_headlines.csv', encoding='utf-8-sig')))

def M(*subs):
    """Row indices whose title contains ANY of the given substrings."""
    out = []
    for i, r in enumerate(ROWS):
        t = r['title']
        if any(s in t for s in subs):
            out.append(i)
    return out

# (section, headline, [title substrings])
B = [
 # ---------------- United Nations ----------------
 ("United Nations", "UNSMIL announces the 4+4 mini-committee reached consensus on the presidential election law in the fourth round of Tunis consultations", ["توصل لجنة الحوار المصغر إلى توافق", "التوصّل إلى توافق بشأن قانون الانتخابات", "consensus on the presidential election", "الاجتماع المصغّر يتوصل إلى توافق", "توافق ليبي جديد حول قانون"]),

 # ---------------- Politics ----------------
 ("Politics", "[US Adviser] Massad Boulos says a Libyan agreement will be signed in Washington with President Trump present if the initiative succeeds, and the transitional phase will not exceed three years", ["الاتفاق الليبي سيُعلن في واشنطن", "Washington to host signing", "Washington Ready to Host"]),
 ("Politics", "[HoR Member] Bin Sharada says the US initiative has moved to implementation and obstructers may be left out of the next phase", ["بن شرادة: المبادرة الأميركية انتقلت"]),
 ("Politics", "[Analyst] Al-Tablaqi says the US initiative is nearing implementation and enjoys the support of a House majority", ["الطبلقي: المبادرة الأميركية تقترب", "الطبلقي: نفوذ طرفي المبادرة"]),
 ("Politics", "[HoR Member] Al-Jahani says the 4+4 consensus on the presidential law paves the way for elections", ["الجهاني: توافق لجنة 4"]),
 ("Politics", "Rashad says the US initiative on Libya is worth studying and exploring", ["رشاد: المبادرة الأميركية بشأن ليبيا تستحق"]),
 ("Politics", "Parallel international moves push to reunify Libya's institutions and launch a new transitional phase", ["تحركات دولية متوازية لإعادة توحيد"]),
 ("Politics", "[Analyst] Mahmoud Qasim asks whether the competing UN and US initiatives can settle the Libyan crisis", ["محمود قاسم يكتب", "هل تقود المبادرات الأممية والأمريكية"]),
 ("Politics", "[Deputy PM] Douma and [HoR-appointed PM] Hammad discuss the south's needs and support for its development projects", ["دومة وحماد يبحثان احتياجات الجنوب"]),
 ("Politics", "HNEC follows up the Benghazi office's preparations for the professional-syndicates and associations elections", ["المفوضية تتابع استعدادات مكتب بنغازي"]),

 # ---------------- Military & Security ----------------
 ("Military & Security", "[Defence Undersecretary] Al-Zoubi discusses unifying the military institution in Washington with Boulos and the AFRICOM deputy commander", ["الزوبي يبحث في واشنطن", "مسؤول ليبي يبحث في واشنطن"]),
 ("Military & Security", "[Defence Undersecretary] Al-Zoubi and the US deputy secretary of state discuss security and defence cooperation", ["الزوبي يبحث مع نائب وزير الخارجية"]),
 ("Military & Security", "[LNA Deputy Commander] Saddam Haftar's foreign tours strengthen Libya's defence partnerships, with a Pakistan visit pointing to advanced military cooperation", ["جولات نائب القائد العام في الخارج", "زيارة صدام حفتر إلى باكستان"]),
 ("Military & Security", "Soldiers are kidnapped in southern Libya near Wadi al-Shati as the General Command stays silent", ["اختطاف عساكر في جنوب ليبيا"]),
 ("Military & Security", "An armed operation in the south disrupts the calm", ["عملية مسلحة» تعكر مسار التهدئة"]),
 ("Military & Security", "Municipalities of Jufra, Tahala and Al-Awaynat condemn the kidnapping of soldiers near Wadi al-Shati and demand the perpetrators be pursued", ["بلديات الجفرة وتهالة والعوينات"]),
 ("Military & Security", "Sabha municipal council denounces criminal attacks on General Command sites and gates", ["بلدي سبها يستنكر الاعتداءات"]),
 ("Military & Security", "Ghat municipal council rejects any attack targeting army and police personnel at security posts and on the borders", ["المجلس البلدي غات", "بلدية غات: نرفض"]),
 ("Military & Security", "General Intelligence Service personnel warn the Presidential Council against touching the agency's unity and reject normalisation", ["منتسبو جهاز المخابرات العامة يوجهون تحذيرا", "ضباط المخابرات الليبية: المساس بوحدة"]),
 ("Military & Security", "Military Police launch a comprehensive security plan across western Libya", ["Military Police launch comprehensive"]),

 # ---------------- Human Rights & Rule of Law ----------------
 ("Human Rights & Rule of Law", "The Public Prosecution orders the detention of the director of the Jadida reform and rehabilitation institution and a judicial officer over the unlawful release of a prisoner", ["مدير مؤسسة الإصلاح والتأهيل (الجديدة", "حبس مدير سجن الجديدة"]),
 ("Human Rights & Rule of Law", "The Attorney General orders the arrest of two Sahara Bank managers over an irregular LYD 800 million credit facility", ["Sahara Bank managers", "Sahara Bank Managers"]),
 ("Human Rights & Rule of Law", "Officials in Ghat municipality are detained over manipulation of a water-tank project and seizure of public funds", ["حبس مسؤولين في بلدية غات", "Ghat Municipality officials"]),
 ("Human Rights & Rule of Law", "Three officials are detained in a forgery case over the supply of medical devices to Zintan", ["حبس 3 مسؤولين في قضية تزوير"]),
 ("Human Rights & Rule of Law", "A Sirte civil-registry employee is detained for granting national ID numbers to six foreigners", ["حبس موظف بالسجل المدني في سرت"]),
 ("Human Rights & Rule of Law", "The Criminal Research Centre trains 150 prosecutors in the basics of forensic medicine", ["مركز البحوث الجنائية يدرب 150"]),
 ("Human Rights & Rule of Law", "687 migrants are returned from Libya to four African countries", ["عودة 687 مهاجرًا"]),
 ("Human Rights & Rule of Law", "An ECOWAS mission concludes its assessment of migrants' conditions in Libya amid calls rejecting resettlement", ["اختتام مهمة «إيكواس» لتقييم وضع المهاجرين"]),
 ("Human Rights & Rule of Law", "[Migration expert] Amteired says tighter control and higher trip costs have cut migrant departures from Libya", ["امطيريد: تشديد الرقابة"]),
 ("Human Rights & Rule of Law", "Security forces raid a boat-making workshop used in migration operations in Sabratha", ["مداهمة «وكر» لصناعة القوارب", "مداهمة وكر لصناعة القوارب"]),
 ("Human Rights & Rule of Law", "The High Council of State holds a dialogue session on irregular migration without compromising national sovereignty", ["الأعلى للدولة يبحث عن معالجات عملية لملف الهجرة", "مجلس الدولة ينظم جلسة حوارية بطرابلس لبحث"]),
 ("Human Rights & Rule of Law", "[Mufti] Al-Gharyani attacks the Structured Dialogue and incites against its women's-rights recommendations", ["الغرياني يهاجم الحوار المهيكل"]),
 ("Human Rights & Rule of Law", "[Activist] Al-Tuwaibi calls the cancellation of Decision 49 a victory for the rule of law and says Palestinians will be treated under foreigner-labour laws", ["الطويبي: إلغاء تفعيل القرار 49"]),
 ("Human Rights & Rule of Law", "The Doctors' Syndicate condemns the assault on medical staff at Abu Salim Emergency Hospital and demands accountability", ["نقابة الأطباء تدين الاعتداء", "«الأطباء» ترفض التعدي", "Doctors Syndicate condemns assault"]),
 ("Human Rights & Rule of Law", "[Hemophilia Society head] Al-Amin says hemophilia patients have gone 10 months without treatment as their condition deteriorates", ["الأمين: مرضى الهيموفيليا بلا علاج"]),
 ("Human Rights & Rule of Law", "Four patients die and others return to dialysis amid a shortage of immunosuppressant drugs", ["وفاة 4 مرضى وعودة آخرين للغسيل"]),
 ("Human Rights & Rule of Law", "A Benghazi workshop with sovereign ministries rejects the UN human-rights report on Libya", ["ورشة ببنغازي ترفض تقرير حقوق الإنسان"]),
 ("Human Rights & Rule of Law", "The Foreign Ministry reviews the Universal Periodic Review outcomes and strengthens national coordination on the human-rights file", ["مخرجات الاستعراض الدوري الشامل"]),

 # ---------------- Economy ----------------
 ("Economy", "A Central Bank source tells Libya Herald that USD 6 billion was injected over two months, with measures expected to curb speculation", ["US$ 6 billion injected", "Injects $6 Billion"]),
 ("Economy", "The Internal Investment Fund and the Audit Bureau agree to reactivate the Mitiga Towers project contract", ["reactivate Mitiga Tow", "restart Mitiga Towers", "Mitiga Sea Towers", "إعادة تفعيل عقد مشروع أبراج البحر"]),
 ("Economy", "First Mall opens as Libya's largest shopping mall after more than 15 years of stop-start construction", ["First Mall opens", "First Mall Opens"]),
 ("Economy", "[Think Tank] The Atlantic Council argues that higher oil production will not save Libya's economy", ["Atlantic Council"]),
 ("Economy", "Libya's oil output nears 1.5 million barrels per day, the highest level since 2013", ["ليبيا تقترب من 1.5 مليون برميل"]),
 ("Economy", "Libya's open borders and price gaps with neighbours hand fuel smugglers huge profits, while Brega says it has taken technical measures to curb smuggling", ["حدود ليبيا المفتوحة وفارق الأسعار", "البريقة: اتخذنا إجراءات فنية لتقليص تهريب"]),
 ("Economy", "Oil prices give up their gains quickly as easing Hormuz tensions calm energy markets", ["هرمز يهدّئ الأسواق", "أسواق الطاقة تتنفس"]),
 ("Economy", "Date producers warn of the consequences of an export ban as more than 7,000 tonnes are stuck between export and storage", ["أكثر من 7 آلاف طن من التمور", "أزمة تمور ليبيا تتصاعد", "Date exporters warn"]),
 ("Economy", "[Economy Minister] says Dbeibah-government restrictions on agricultural and fish exports are temporary to protect the market", ["اقتصاد الدبيبة: قيود تصدير المنتجات"]),
 ("Economy", "The Economy Ministry issues a regulation governing the granting of foreign commercial agencies in Libya", ["لائحة تنظيم منح الوكالات التجارية", "لائحة ضوابط منح الوكالات"]),
 ("Economy", "A German company wins two contracts to supply Libya's first advanced vertical cement mills", ["شركة ألمانية تفوز بعقدين"]),
 ("Economy", "The World Food Programme says Libya's spending basket fell to 1,180 dinars after April's jump", ["سلة الإنفاق في ليبيا تتراجع إلى 1180"]),
 ("Economy", "[PM] Abdulhamid Dbeibah receives the head of the Russian-Libyan Business Council to discuss strengthening cooperation", ["receives head of Russian-Libyan Business"]),
 ("Economy", "The Libya Businessmen Forum for Development and Reconstruction opens with broad economic participation", ["منتدى رجال أعمال ليبيا للتنمية", "منتدى رجال الأعمال ليبيا للتنمية"]),
 ("Economy", "The Industry Ministry launches a 100-day sector development plan", ["100-Day Sector Development", "100-day plan for developing"]),
 ("Economy", "Misrata Chamber of Commerce takes part in the Tunisia Investment Forum in Tunis", ["Misrata Chamber of Commerce participates"]),
 ("Economy", "The National Development Agency discusses completing a 500-unit housing project in Hrawa", ["500 Housing Units Project in Hrawa"]),
 ("Economy", "Libya's passport rises to 93rd in the global mobility ranking", ["الجواز في المرتبة 93"]),

 # ---------------- Environment ----------------
 ("Environment", "Deliberate sabotage targets high-voltage power-transmission lines in Wadi al-Shati", ["رصد أعمال تخريب متعمدة استهدفت خطوط نقل الكهرباء", "رصد أعمال تخريب استهدفت خطوط الضغط العالي"]),
 ("Environment", "Rehabilitation of damaged power towers in the south enters its final stages", ["أعمال تأهيل أبراج الكهرباء في الجنوب"]),
 ("Environment", "The electricity company says unregulated urban sprawl obstructed the repair of a main cable fault in Benghazi", ["التوسع العمراني العشوائي أعاق إصلاح عطل كابل"]),
 ("Environment", "The Local Government Ministry takes part in a workshop on waste management and environmental sanitation", ["waste management"]),

 # ---------------- Regional & International ----------------
 ("Regional & International", "Libya is elected vice-president of the African Union and affirms its commitment to cooperation", ["نائباً لرئيس الاتحاد الأفريقي", "نائبًا ثالثًا لرئيس الاتحاد الأفريقي"]),
 ("Regional & International", "An Indian diplomatic delegation arrives in Tripoli to discuss developing bilateral cooperation across sectors", ["وفد دبلوماسي هندي يصل طرابلس"]),
 ("Regional & International", "[Justice Minister] Halima Ibrahim takes part in the International Legal Forum in St Petersburg", ["وزيرة العدل تشارك في فعاليات المنتدى القانوني"]),
 ("Regional & International", "[HoR Speaker] Aguila Saleh takes part in the meeting of Arab parliament speakers in Cairo", ["رئيس مجلس النواب الليبي يشارك في اجتماع رؤساء البرلمانات", "مجلس النواب يشارك باجتماع «البرلمانات العربية»"]),

 # ---------------- Varieties ----------------
 ("Varieties", "Libya races to save its ancient Greek ruins (Cyrene and Apollonia) as conflict and climate threaten UNESCO heritage sites", ["ancient Greek ruins", "لإنقاذ قورينا وأبولونيا"]),
 ("Varieties", "A YouTube video leads to the rediscovery of sand cats in Libya, where they had not been known to live", ["sand cat", "Sand Cats In Libya", "قط الرمال"]),
 ("Varieties", "Benghazi is named the permanent base for the union of Maghreb journalists", ["Permanent Base for Maghreb Journalists"]),
 ("Varieties", "The Tourism and Antiquities Ministry continues its efforts to establish a regional museum in Shahat", ["إنشاء المتحف الإقليمي بمدينة شحات"]),
 ("Varieties", "More than 134,000 students begin Libya's secondary-school certificate examinations as the Education Ministry tightens anti-cheating measures", ["secondary school certificate", "امتحانات الشهادة الثانوية", "التربية تشدد إجراءات الامتحانات"]),
 ("Varieties", "The youth-council elections committee declares its readiness to run the vote in 28 municipalities", ["لجنة انتخابات الشباب تعلن جاهزيتها"]),
 ("Varieties", "Libya opens its Arab U-18 basketball campaign against Tunisia", ["البطولة العربية لكرة السلة تحت 18"]),
 ("Varieties", "Forty-eight lifters compete for the titles of Libya's youth weightlifting championship in Tripoli", ["48 رباعًا يتنافسون"]),
 ("Varieties", "[Feature] Libyan doctor and artist 'Amido' turns street murals into a visual language", ["الطبيب والفنان الليبي «أميدو»"]),
]

SECTION_ORDER = ["United Nations","Politics","Military & Security","Human Rights & Rule of Law","Economy","Environment","Regional & International","Varieties"]

def sources_for(idxs):
    seen={}; out=[]
    for i in idxs:
        r=ROWS[i]; name=canonicalize_outlet(r['source_name'])
        key=name.casefold()
        if key in seen: continue
        seen[key]=1
        out.append(HeadlineSource(name=name, language=r['language'], url=r['url']))
    out.sort(key=lambda s: s.language!='en')
    return out

secmap={s:[] for s in SECTION_ORDER}
VERIFY=[]
for sec,text,subs in B:
    idxs=M(*subs)
    VERIFY.append((sec,text,idxs))
    secmap[sec].append(ReportHeadline(text=text, sources=sources_for(idxs)))

report=StructuredReport(report_date="25-28 June", sections=[
    ReportSection(name=s, subsections=[ReportSubsection(name="", headlines=secmap[s])]) for s in SECTION_ORDER if secmap[s]
], is_draft=False)
out="output/Libya_News_Headlines_25-28_June_2026_PICS.docx"
write_word_report(report, [], out)
print(f"WROTE {out} | bullets={report.total_headlines()}")
for s in SECTION_ORDER: print(f"   {s}: {len(secmap[s])}")
if __name__=='__main__' and len(__import__('sys').argv)>1 and __import__('sys').argv[1]=='-v':
    for sec,text,idxs in VERIFY:
        flag=' <<NO MATCH' if not idxs else (' <<MANY' if len(set(ROWS[i]['source_name'] for i in idxs))>8 else '')
        print(f"\n[{sec[:4]}] {text[:60]} ({len(idxs)} rows){flag}")
        for i in idxs[:6]: print(f"     ({ROWS[i]['source_name']}) {ROWS[i]['title'][:60]}")
