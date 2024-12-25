from django.shortcuts import render

def displayHomePage(request):

    masterDict = {
        'key' : 'value'
    }

    return render(request, 'mysite/home.html', masterDict)


def displayProfessionalPage(request):
    return render(request, 'mysite/sect_professional.html')

def displayAcademicPage(request):
    return render(request, 'mysite/sect_academic.html')

def displayMusicPage(request):
    return render(request, 'mysite/sect_music.html')

def displayArticlesPage(request):
    return render(request, 'mysite/sect_articles.html')

def displayArticleDetail(request, article_name):
    try:
        return render(request, f'mysite/../articles/{article_name}.html')
    except TemplateDoesNotExist:
        raise Http404("Article not found.")

def displayContactPage(request):

    concerts_seen = {
        "2010/2011": ["Karnivool", "Asha Bhosle", "Katatonia", "Junkyard Groove", "The Raghu Dixit Project"],
        "2012": ["Guns N' Roses", "Simple Plan", "Thermal and a Quarter"],
        "2013": ["Baiju Dharmajan Syndicate", "Neal Morse with Mike Portnoy"],
        "2014": ["The F-16's", "Epica"],
        "2015": ["Thermal and a Quarter", "Slash with Myles Kennedy!!"],
        "2016": ["Indian Jam Project", "The Local Train (Twice)", "The Aristocrats", "Skrat", "Crown the Empire"],
        "2017": ["When Chai Met Toast", "Lagori", "YouTube Fan Fest", "Abhishek Gurung Collective", "Dream Theater", "Sparsh", "The F-16's", "Haken"],
        "2018": ["The Local Train", "Amit Trivedi & Others", "The Raghu Dixit Project", "The Local Train", "My HRC Gig"],
        "2019": ["Soulmate", "TheBasementSessions", "The Local Train", "Rhythm Shaw ft. others", "Soulmate", "The Local Train"],
        "2020": ["lol"],
        "2021": ["John Mayer live on IG :)"],
        "2022": ["John Mayer", "Josh Radnor", "Mike Dawes live on IG :)"],
        "2023": ["Khalid and Ed Sheeran", "Guns N' Roses and The Pretenders", "Eric Johnson", "Babish (Book Tour)", "Periphery and Mike Dawes", "Plini"],
        "2024": ["Cory Wong", "Juice", "SOJA and Arise Roots", "Slash", "Steel Panther", "Coheed and Cambria", "Green Day and Smashing Pumpkins", "coolcoolcool"],
    }


    return render(request, 'mysite/sect_contact.html', {'collections': concerts_seen})

def handlerView404(request):
    return render(request, 'mysite/404_handler.html')
