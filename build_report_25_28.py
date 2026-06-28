"""25-28 June 2026 PICS report, authored by Claude (editor) from the live scrape.
Each bullet lists the data-row indices it covers; sources/URLs are pulled from
those rows so attribution can't drift. Run to render the .docx.
"""
import csv
from utils.models import HeadlineSource, ReportHeadline, ReportSection, ReportSubsection, StructuredReport
from utils.outlets import canonicalize_outlet
from utils.exports import write_word_report

ROWS = list(csv.DictReader(open('output/libya_media_headlines.csv', encoding='utf-8-sig')))

# (section, headline, [row indices])
B = [
 # ---------------- United Nations ----------------
 ("United Nations", "UNSMIL announces the 4+4 mini-committee reached consensus on the presidential election law in the fourth round of Tunis consultations", [427,409,419,428,430]),

 # ---------------- Politics ----------------
 ("Politics", "[US Adviser] Massad Boulos says a Libyan agreement will be signed in Washington with President Trump present if the initiative succeeds, and the transitional phase will not exceed three years", [31,32,136,158,135,196]),
 ("Politics", "Parallel international moves push to reunify Libya's institutions and launch a new transitional phase", [185,338]),
 ("Politics", "A last-minute agreement and a high-risk election timeline draw French interest in the Trump deal amid the three-presidencies' manoeuvring", [407,408]),
 ("Politics", "[Analyst] Mahmoud Qasim asks whether the competing UN and US initiatives can settle the Libyan crisis", [52,397]),
 ("Politics", "[Commentator] Mustafa Bakri says the LNA deputy commander holds a consensual approach and wide room for dialogue among Libyan parties", [258]),

 # ---------------- Military & Security ----------------
 ("Military & Security", "[Defence Undersecretary] Al-Zoubi discusses unifying the military institution in Washington with Boulos and the AFRICOM deputy commander", [351,314]),
 ("Military & Security", "[Defence Undersecretary] Al-Zoubi and the US deputy secretary of state discuss security and defence cooperation", [232]),
 ("Military & Security", "[LNA Deputy Commander] Saddam Haftar's foreign tours strengthen Libya's defence partnerships, with a Pakistan visit pointing to advanced military cooperation", [164,339]),
 ("Military & Security", "Soldiers are kidnapped in southern Libya near Wadi al-Shati as the General Command stays silent", [114,115]),
 ("Military & Security", "An armed operation in the south disrupts the calm", [242,243]),
 ("Military & Security", "Municipalities of Jufra, Tahala and Al-Awaynat condemn the kidnapping of soldiers near Wadi al-Shati and demand the perpetrators be pursued", [132]),
 ("Military & Security", "Sabha municipal council denounces criminal attacks on General Command sites and gates", [209]),
 ("Military & Security", "Ghat municipal council rejects any attack targeting army and police personnel stationed at security posts and on the borders", [33,155,156]),
 ("Military & Security", "General Intelligence Service personnel warn the Presidential Council against touching the agency's unity and reject normalisation", [60,162,163]),
 ("Military & Security", "Military Police launch a comprehensive security plan across western Libya", [21,22]),

 # ---------------- Human Rights & Rule of Law ----------------
 ("Human Rights & Rule of Law", "The Public Prosecution orders the detention of the director of the Jadida reform and rehabilitation institution and a judicial officer over the unlawful release of a prisoner", [49,59]),
 ("Human Rights & Rule of Law", "The Attorney General orders the arrest of two Sahara Bank managers over an irregular LYD 800 million credit facility", [39,40]),
 ("Human Rights & Rule of Law", "The Public Prosecution orders the detention of two Ghat municipality officials in a water-project corruption case", [18]),
 ("Human Rights & Rule of Law", "687 migrants are returned from Libya to four African countries", [160,161]),
 ("Human Rights & Rule of Law", "An ECOWAS mission concludes its assessment of migrants' conditions in Libya amid calls rejecting resettlement", [153,154]),
 ("Human Rights & Rule of Law", "Security forces raid a boat-making workshop used in migration operations in Sabratha", [300,286]),
 ("Human Rights & Rule of Law", "The High Council of State holds a dialogue session on irregular migration without compromising national sovereignty", [145,146,134]),
 ("Human Rights & Rule of Law", "The Presidential Council's Civil Society Commission calls for a comprehensive national strategy on irregular migration", [35]),
 ("Human Rights & Rule of Law", "The Doctors' Syndicate condemns the assault on medical staff at Abu Salim Emergency Hospital and demands accountability", [51,228,109,17]),
 ("Human Rights & Rule of Law", "A Benghazi workshop with sovereign ministries rejects the UN human-rights report on Libya", [14]),
 ("Human Rights & Rule of Law", "The Foreign Ministry reviews the Universal Periodic Review outcomes and strengthens national coordination on the human-rights file", [70]),

 # ---------------- Economy ----------------
 ("Economy", "A Central Bank source tells Libya Herald that USD 6 billion was injected over two months, with measures expected to curb speculation", [414,415]),
 ("Economy", "The Internal Investment Fund and the Audit Bureau agree to reactivate the Mitiga Towers project contract with the implementing company", [330,263,264,331]),
 ("Economy", "First Mall opens as Libya's largest shopping mall after more than 15 years of stop-start construction", [57,58]),
 ("Economy", "[Think Tank] The Atlantic Council argues that higher oil production will not save Libya's economy", [97,98]),
 ("Economy", "Libya's open borders and price gaps with neighbours hand fuel smugglers huge profits", [176,175]),
 ("Economy", "Brega says it has taken technical measures to curb fuel smuggling and that the file needs a national effort", [174]),
 ("Economy", "Oil prices give up their gains quickly as easing Hormuz tensions calm energy markets", [291,292,6,7]),
 ("Economy", "Date producers warn of the consequences of an export ban as Libya's surplus crisis mounts ahead of the new season", [323,337,80,81]),
 ("Economy", "The Economy Ministry issues a regulation governing the granting of foreign commercial agencies in Libya", [288,283]),
 ("Economy", "[PM] Abdulhamid Dbeibah receives the head of the Russian-Libyan Business Council to discuss strengthening cooperation", [42]),
 ("Economy", "The Libya Businessmen Forum for Development and Reconstruction opens with broad economic participation", [388,224]),
 ("Economy", "The Industry Ministry launches a 100-day sector development plan", [334,333]),
 ("Economy", "Misrata Chamber of Commerce takes part in the Tunisia Investment Forum in Tunis", [50]),
 ("Economy", "The National Development Agency discusses completing a 500-unit housing project in Hrawa", [332]),
 ("Economy", "Libya's passport rises to 93rd in the global mobility ranking", [197,198,199]),

 # ---------------- Environment ----------------
 ("Environment", "Deliberate sabotage targets high-voltage power-transmission lines in Wadi al-Shati", [272,282]),
 ("Environment", "The electricity company says unregulated urban sprawl obstructed the repair of a main cable fault in Benghazi", [327]),
 ("Environment", "IAEA experts conclude a technical visit assessing the readiness of Libya's radiotherapy centres", [265]),
 ("Environment", "The Local Government Ministry takes part in a workshop on waste management and environmental sanitation", [45,46]),
 ("Environment", "Thunderstorms and strong winds strike the Silk area south of Sloug", [92]),

 # ---------------- Regional & International ----------------
 ("Regional & International", "Libya is elected vice-president of the African Union and affirms its commitment to cooperation", [352,353]),
 ("Regional & International", "An Indian diplomatic delegation arrives in Tripoli to discuss developing bilateral cooperation across sectors", [34,38]),
 ("Regional & International", "[Justice Minister] Halima Ibrahim takes part in the International Legal Forum in St Petersburg", [227,236]),
 ("Regional & International", "[HoR Speaker] Aguila Saleh takes part in the meeting of Arab parliament speakers in Cairo", [142,207]),

 # ---------------- Varieties ----------------
 ("Varieties", "Libya races to save its ancient Greek ruins as conflict and climate threaten UNESCO heritage sites", [296,93,369]),
 ("Varieties", "A YouTube video leads to the rediscovery of sand cats in Libya, where they had not been known to live", [365]),
 ("Varieties", "Benghazi is named the permanent base for the union of Maghreb journalists", [83,85]),
 ("Varieties", "The Tourism and Antiquities Ministry continues its efforts to establish a regional museum in Shahat", [308]),
 ("Varieties", "More than 134,000 students begin Libya's secondary-school certificate examinations as the Education Ministry tightens anti-cheating measures", [19,20,63,64,210,211]),
 ("Varieties", "The youth-council elections committee declares its readiness to run the vote in 28 municipalities", [118,119,120]),
 ("Varieties", "Libya opens its Arab U-18 basketball campaign against Tunisia", [192,193]),
 ("Varieties", "Forty-eight lifters compete for the titles of Libya's youth weightlifting championship in Tripoli", [200]),
 ("Varieties", "[Feature] Libyan doctor and artist 'Amido' turns street murals into a visual language", [3,4]),
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
    out.sort(key=lambda s: s.language!='en')  # English first
    return out

secmap={s:[] for s in SECTION_ORDER}
for sec,text,idxs in B:
    secmap[sec].append(ReportHeadline(text=text, sources=sources_for(idxs)))

report=StructuredReport(report_date="25-28 June", sections=[
    ReportSection(name=s, subsections=[ReportSubsection(name="", headlines=secmap[s])]) for s in SECTION_ORDER if secmap[s]
], is_draft=False)

out="output/Libya_News_Headlines_25-28_June_2026_PICS.docx"
write_word_report(report, [], out)
print(f"WROTE {out} | bullets={report.total_headlines()}")
for s in SECTION_ORDER:
    print(f"   {s}: {len(secmap[s])}")
