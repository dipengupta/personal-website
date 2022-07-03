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

def displayContactPage(request):
    return render(request, 'mysite/sect_contact.html')