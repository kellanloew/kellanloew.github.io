from django import template
from AccountsApp.models import AppProps, AllAppPreferences, BandsPreferences, BudgetPreferences, MoviesPreferences, HabitsPreferences, RecipesPreferences, RestaurantsPreferences, WeatherPreferences, TrafficPreferences, CraigslistPreferences, MessagesPreferences, PodcastsPreferences, NewsPreferences, SpacePreferences, all_apps, create_prefs
from django.contrib.auth.models import User

register = template.Library()

# For each app in the app manager on the profile page
class Manager():
    def __init__(self, name, icon, description, contributors, button1, button2, button3, color):
        self.name = name
        self.icon = icon
        self.description = description
        self.contributors = contributors
        self.button1 = button1
        self.button2 = button2
        self.button3 = button3
        self.color = color
#For each app on the homepage dashboard
class HomeApps():
    def __init__(self, title, icon, url):
        self.title = title
        self.icon = icon
        self.url = url

#This tag is for displaying app details on the app manager
# Register this function as a custom Django tag. Parameter is the template that the tag will render.
# Then, we can load this tag with the function name below on any HTML page adn this tag wil be loaded
@register.inclusion_tag('CustomTags/app_manager.html')
def display_apps(request):
    #Get list of all apps and their details
    db_all = AppProps.objects.all()
    allApps = []
    #Create instances of Manager with app details for each app
    for app in db_all:
        curApp = Manager(app.app_name, app.icon, app.description, app.contributors, app.button1, app.button2, app.button3, app.color)
        allApps.append(curApp)

    all_apps_preferences = []

    for app in all_apps: #Gets the user's preferences for each app
        #Get list of all preference values associated with current user
        cur_prefs = app.objects.filter(user_id = request.user.id).values_list()
        cur_app = app() #Create instance of current AppPreference
        
        #Loop through the preference values for each button, assigning the values to the respective properties of the instance
        counter = 0
        for pref in enumerate(cur_prefs[0]):
            if type(pref) != int: #Excludes the userid column
                if counter == 1: #Assign properties to the instance depending on which properties we're on
                    cur_app.offOn = pref[1]
                elif counter == 2:
                    cur_app.button1 = pref[1]
                elif counter == 3:
                    cur_app.button2 = pref[1]
                elif counter == 4:
                    cur_app.button3 = pref[1]
            counter += 1
        all_apps_preferences.append(cur_app) #Add to list of app preference instances
    
    both_lists = zip(allApps, all_apps_preferences)

    return {'apps': both_lists}

#This function displays only those apps that the user has decided to show
@register.inclusion_tag('CustomTags/homepage_apps.html')
def show_active_apps(request):
    #This can be deleted after Development. This creates preference tables for those whose accounts were made before this was implemented
    #===================
    if not BandsPreferences.objects.filter(user_id=request.user.userprofile.user_id):
        create_prefs(request.user)
    #===================
    active_apps = []
    all = AppProps.objects.all()  #Get list of all apps and their details
    for prop, app in zip(all, all_apps):
        name = prop.app_name
        #Call function to get details for current app
        currentApp = get_details_HmPg(name, app, request.user.id)
        if currentApp: #Add to list of active apps if the function returns an app
            active_apps.append(currentApp)
    
    return {'apps': active_apps}

#Returns details for an app if user has selected this app to be active        
def get_details_HmPg(name, app, cur_user):
    preference = app.objects.get(user=cur_user)#Find current user's preferences for this app
    if preference.offOn == True: #If this app is to be displayed:
        row = AppProps.objects.get(app_name=name) #Find details for this app
        title = row.title
        icon = row.icon
        url = row.url
        cur_app = HomeApps(title, icon, url)
        return cur_app