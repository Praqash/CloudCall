from __future__ import division
from django.http import HttpResponse
from django.shortcuts import render
from PureCloudPlatformClientV2.rest import ApiException
import PureCloudPlatformClientV2
import csv
import datetime



CLIENT_ID = "4f850f92-fbc8-4f13-ad52-5941d2cf6add"
CLIENT_SECRET = "hR_fdDf2dCUzMW4TjLKBLRSGa7bKaLU98IJszo7zRTk"
ENVIRONMENT = "mypurecloud.de" 
region = PureCloudPlatformClientV2.PureCloudRegionHosts["eu_central_1"]
PureCloudPlatformClientV2.configuration.host = region.get_api_host()
api_client = PureCloudPlatformClientV2.api_client.ApiClient().get_client_credentials_token(CLIENT_ID, CLIENT_SECRET)
user_api_instance = PureCloudPlatformClientV2.UsersApi(api_client)
scim_api_instance = PureCloudPlatformClientV2.SCIMApi(api_client)
routing_api_instance = PureCloudPlatformClientV2.RoutingApi(api_client)
authorization_api_instance = PureCloudPlatformClientV2.AuthorizationApi(api_client)
group_api_instance = PureCloudPlatformClientV2.GroupsApi(api_client)
license_api_instance=PureCloudPlatformClientV2.LicenseApi(api_client)
locations_api_instance=PureCloudPlatformClientV2.LocationsApi(api_client)







def index(request):
    return render(request, 'CloudApp/index.html')

def filter_agent(request):
    division =[]
    dname=[]

    response = authorization_api_instance.get_authorization_divisions().page_count
    for i in range(1, response+1):
        response = authorization_api_instance.get_authorization_divisions(page_number=i).entities
        for i in response:
            division.append(i.name + ':' + i.id)
            division = list(set(division))
            division.sort()
    
        for div in division:
            dname.append(div.split(':'))
            context={"dname": dname}
    return render(request, 'CloudApp/filter_agent.html',context)
    
def filter_queue(request):
    division =[]
    dname=[]
    res = routing_api_instance.get_routing_queues_divisionviews_all()
    for p in range(1,(res.page_count)+1):
         res = routing_api_instance.get_routing_queues_divisionviews_all(page_number=p).entities
         for r in res:
            division.append(r.division.name + ':' + r.division.id)
    division= list(set(division))
    division.sort()
    for name in division:
        dname.append(name.split(':'))
    context={"dname": dname}
    return render(request, 'CloudApp/filter_queue.html',context)


def filter_agent_role(request):
    division =[]
    dname=[]
    res = routing_api_instance.get_routing_queues_divisionviews_all()
    for p in range(1,(res.page_count)+1):
         res = routing_api_instance.get_routing_queues_divisionviews_all(page_number=p).entities
         for r in res:
            division.append(r.division.name + ':' + r.division.id)
    division= list(set(division))
    division.sort()
    for name in division:
        dname.append(name.split(':'))
    context={"dname": dname}
    return render(request, 'CloudApp/filter_agent_role.html',context)

    
    
    
def agent_report(request):
    display_name=[]
    user_name=[]
    language=[]
    user_id=[]
    queues=[]
    skills=[]
    dicts={}
    data=[]
    div=[]
   
    
    division= request.POST.get("dname")
    division = division.split(':')
    division_name=division[0]
    division_id=division[1]
    response= (scim_api_instance.get_scim_users(count= 0))  # at count = 0, it gives 'total_results' json object, this object holds count number.
    count= response.total_results
    name= ((scim_api_instance.get_scim_users(count=count, attributes='displayName,userName', filter = f"division eq {division_name}")))
    
    
    for x in name.resources:
        user_id.append(x.id)
        display_name.append(x.display_name)
        user_name.append(x.user_name)
    
    
    for i in user_id:
        x=user_api_instance.get_user_queues(user_id=i).entities
        if x:
            queues.append([x.name for x in x])
        else:
            queues.append(None)
      
    

        x=user_api_instance.get_user_routingskills(i).entities
        if x:
            skills.append([x.name for x in x])
        else:
            skills.append(None)    
    
    
    
        x=user_api_instance.get_user_routinglanguages(i).entities
        if x:
            language.append([x.name for x in x])
        else:
            language.append(None)
    
    
        div.append(division_name)
        
        
    data.append(display_name)
    data.append(user_name)
    data.append(div)
    data.append(queues)
    data.append(skills)
    data.append(language)
    
    request.session['data'] = data
    request.session['user_id'] = user_id
    
    for i in range (1,len(user_id)+1):
        dicts[i] = [display_name[i-1], user_name[i-1], div[i-1], queues[i-1], skills[i-1], language[i-1]]        
    context= {'dicts': dicts, 'range': range(len(user_id))}
    return render(request, 'CloudApp/agent_report.html', context)
        

def queue_report(request):
    evaluation_method=[]
    routing_method=[]
    queues_id=[]
    queues=[]
    agents=[]
    dicts={}
    temp=[]
    data1=[]
    
    division= request.POST.get("dname")
    division = division.split(':')
    division_name=division[0]
    division_id=division[1]
    response=routing_api_instance.get_routing_queues_divisionviews().page_count
    for i in range(response):
        response=routing_api_instance.get_routing_queues_divisionviews(division_id=division_id, page_number=i).entities
        for j in response:
                temp.append(j.name + ':' + j.id)
    temp = (list(set(temp)))
    temp.sort()
    
    for i in temp:
        x= i.split(':')
        queues.append(x[0])
        queues_id.append(x[1]) 
           
    for i in queues_id:
        x= routing_api_instance.get_routing_queue_members(queue_id=i).entities
        if x:
            agents.append([x.name for x in x])
        else:
            agents.append(None)
        
       
    for i in queues_id:
        x= routing_api_instance.get_routing_queue(queue_id=i)
        if x.skill_evaluation_method =='ALL':
            evaluation_method.append("All Skills Matching")
        elif x.skill_evaluation_method =='BEST':
            evaluation_method.append("Best Available Skills")
        else:
            evaluation_method.append("Disregard Skills, next agent")
            
            
    for i in queues_id:
        x= routing_api_instance.get_routing_queue(queue_id=i)
        if x.routing_rules and x.bullseye:
            routing_method.append("Prefered Agent(Bullseye Routing)")
        elif x.routing_rules:
            routing_method.append("Prefered Agent(Standard Routing)")
        if not x.routing_rules and x.bullseye:
            routing_method.append("Bulleseye Routing")
        else:
            routing_method.append("Standard Routing")
    
    request.session['data1'] = data1

    for i in range (1,len(queues)+1):
        dicts[i] = [queues[i-1],division_name, agents[i-1], evaluation_method[i-1], routing_method[i-1]]   
    context= {'dicts': dicts, 'range': range(len(queues))}
    return render(request, 'CloudApp/queue_report.html', context)

def filter(request):
    divisions=[]
    locations=[]
    groups=[]
    roles=[]
    temp=[]

    if request.method == "POST":
        filter=request.POST.get("filter")
        if filter=="Division":
            response = authorization_api_instance.get_authorization_divisions().page_count
            for i in range(1, response+1):
                response = authorization_api_instance.get_authorization_divisions(page_number=i).entities
                for i in response:
                    temp.append(i.name + ':' + i.id)
                temp = list(set(temp))
                temp.sort()
    
            for div in temp:
                divisions.append(div.split(':'))
            context={"var": divisions,
                     "filter":filter}
            return render(request, 'CloudApp/filter_agent_role.html', context)
        elif filter=="Roles":
            response = authorization_api_instance.get_authorization_roles().page_count
            for i in range(1,response+1):
                response=authorization_api_instance.get_authorization_roles(page_number = i).entities
                for i in response:
                    temp.append(i.name + ':' + i.id)
            temp = (list(set(temp)))
            temp.sort()
            for role in temp:
                    roles.append(role.split(':'))
            context={"var": roles,
                     "filter":filter}
            return render(request, 'CloudApp/filter_agent_role.html', context)
        elif filter=="Location":
            response = locations_api_instance.get_locations().entities #Here page_count is none
            for i in response:
                temp.append(i.name + ':' + i.id)
            temp = (list(set(temp)))
            temp.sort()
            for location in temp:
                    locations.append(location.split(':'))
            context={"var": locations,
                     "filter": filter}
            return render(request, 'CloudApp/filter_agent_role.html', context)
        elif filter == "Group":
            response= group_api_instance.get_groups().page_count
            for i in range(1,response+1):
                response=group_api_instance.get_groups(page_number = i).entities
                for i in response:
                    temp.append(i.name + ':' + i.id)
            temp = (list(set(temp)))
            temp.sort()
            for group in temp:
                    groups.append(group.split(':'))
            context={"var": groups,
                     "filter":filter}
            return render(request, 'CloudApp/filter_agent_role.html', context)
            
        
 
    

def agent_role_report(request):
    user_id=[]
    licenses_id=[]
    acd_skills=[]
    utilization=[]
    licenses=[]
    location=[]
    division=[]
    display_name=[]
    user_name=[]
    group_id=[]
    dicts={}
    active=[]
    var=[]
    roles=[]
    groups=[]
    l=0
    if request.method == "POST":
        var=request.POST.get("var")
        var= var.split(':')
        name= var[0]
        Id= var[1]
        filter= var[2]
        context= {"var":var}
        if filter == "Division":
            response= (scim_api_instance.get_scim_users(count= 0))  # at count = 0, it gives 'total_results' json object, this object holds count number.
            count= response.total_results
            response= ((scim_api_instance.get_scim_users(count=count, attributes='displayName,active,userName,roles', filter = f"division eq {name}")))
            for x in response.resources:
                user_id.append(x.id)
                display_name.append(x.display_name)
                user_name.append(x.user_name)
                active.append(x.active)
            x = license_api_instance.get_license_users().page_count
            for p in range(1,(x+1)):
                x = license_api_instance.get_license_users(page_number=p).entities
                for i in x:
                    licenses_id.append(i.id + ':' + str(i.licenses)) 
            for i in licenses_id:
                var.append(i.split(':'))
            while l < len(user_id):
                j= user_id[l]
                for k in range(len(var)):                        
                    if j== var[k][0]:
                        licenses.append(var[k][1])
                l=l+1
    
           
            for id in user_id:
                x = scim_api_instance.get_scim_user(attributes='groups', user_id=id)
                if x.groups:
                    group_id.append([i.value for i in x.groups])
                else:
                    group_id.append([None])
            for a in group_id:
                if a[0]== None:
                    groups.append(None)
                else:
                    groups.append([group_api_instance.get_group(group_id=i).name for i in a])
           
                    
            for id in user_id: 
                division.append(name)
                x = user_api_instance.get_user_roles(user_id=id).roles
                if x:
                    roles.append([x.name for x in x])
                else:
                    roles.append(None)
                
                x = routing_api_instance.get_routing_user_utilization(user_id=id).utilization
                utilization.append([x for x in x])
                
                x = user_api_instance.get_user(user_id=id, expand= "locations")
                if x.locations !=[]:
                    for i in x.locations:
                        location_id= i.location_definition.id
                        location.append(locations_api_instance.get_location(location_id=location_id).name)
                else:
                    location.append(None)
                x = user_api_instance.get_user_routingskills(user_id=id).entities
                if x:
                    acd_skills.append([x.name for x in x])
                else:
                    acd_skills.append(None)   
            for i in range (1,len(user_id)+1):
                dicts[i] = [display_name[i-1], user_name[i-1], active[i-1], acd_skills[i-1], utilization[i-1], location[i-1], licenses[i-1], groups[i-1], roles[i-1], division[i-1]]        
                context= {'dicts': dicts, 'filter':filter, 'name':name, 'range': range(len(user_id))}
            return render(request, 'CloudApp/agent_role_report.html', context)
        
        elif filter == "Roles":
            page_count= authorization_api_instance.get_authorization_role_users(role_id=Id).page_count
            if page_count != None:
                for i in range(1, page_count+1):
                    response=authorization_api_instance.get_authorization_role_users(page_number=i, role_id=Id).entities
                    for res in response:
                        user_id.append(res.id)
            else:
                response=authorization_api_instance.get_authorization_role_users(page_number=0, role_id=Id).entities
                for res in response:
                    user_id.append(res.id)
            x = license_api_instance.get_license_users().page_count
            for p in range(1,(x+1)):
                x = license_api_instance.get_license_users(page_number=p).entities
                for i in x:
                    licenses_id.append(i.id + ':' + str(i.licenses)) 
            for i in licenses_id:
                var.append(i.split(':'))
            while l < len(user_id):                            
                j= user_id[l]
                for k in range(len(var)):
                    if j== var[k][0]:
                        licenses.append(var[k][1])
                l=l+1
            for id in user_id:
                x = scim_api_instance.get_scim_user(user_id=id).urnietfparamsscimschemasextensionenterprise2_0_user
                division.append(x.division)
            
            for id in user_id:
                x = scim_api_instance.get_scim_user(attributes='groups', user_id=id)
                if x.groups:
                    group_id.append([i.value for i in x.groups])
                else:
                    group_id.append([None])
            for a in group_id:
                if a[0]== None:
                    groups.append(None)
                else:
                    groups.append([group_api_instance.get_group(group_id=i).name for i in a])
           
            for id in user_id:
                roles.append(name)
                x = scim_api_instance.get_scim_user(attributes='displayName, groups, active,userName', user_id=id)
                display_name.append(x.display_name)
                user_name.append(x.user_name)
                active.append(x.active)
                x = routing_api_instance.get_routing_user_utilization(user_id=id).utilization
                utilization.append([x for x in x])
            
                x = user_api_instance.get_user_routingskills(user_id=id).entities
                if x:
                    acd_skills.append([x.name for x in x])
                else:
                    acd_skills.append(None) 
                
                x = user_api_instance.get_user(user_id=id, expand= "locations")
                if x.locations !=[]:
                    for i in x.locations:
                        location_id= i.location_definition.id
                        location.append(locations_api_instance.get_location(location_id=location_id).name)
                else:
                    location.append(None)
        
            for i in range (1,len(user_id)+1):
                dicts[i] = [display_name[i-1], user_name[i-1], active[i-1], acd_skills[i-1], utilization[i-1], location[i-1], licenses[i-1],groups[i-1], roles[i-1], division[i-1]]        
                context= {'dicts': dicts, 'filter':filter, 'name':name, 'range': range(len(user_id))}
            return render(request, 'CloudApp/agent_role_report.html', context)
        
        elif filter == "Group":
            response= group_api_instance.get_group_individuals(group_id= Id).entities
            for x in response:
                user_id.append(x.id)
            x = license_api_instance.get_license_users().page_count
            for p in range(1,(x+1)):
                x = license_api_instance.get_license_users(page_number=p).entities
                for i in x:
                    licenses_id.append(i.id + ':' + str(i.licenses)) 
            for i in licenses_id:
                var.append(i.split(':'))
            while l < len(user_id):
                j= user_id[l]
                for k in range(len(var)):                            
                    if j== var[k][0]:
                        licenses.append(var[k][1])
                l=l+1
                
            for id in user_id:
                x = scim_api_instance.get_scim_user(user_id=id).urnietfparamsscimschemasextensionenterprise2_0_user
                division.append(x.division)
            
                
            for id in user_id:
                groups.append(name)
                x = user_api_instance.get_user_roles(user_id=id).roles
                if x:
                    roles.append([x.name for x in x])
                else:
                    roles.append(None)
                x = scim_api_instance.get_scim_user(attributes='displayName,active,userName,roles', user_id=id)
                display_name.append(x.display_name)
                active.append(x.active)
                user_name.append(x.user_name)
                
                
                x = routing_api_instance.get_routing_user_utilization(user_id=id).utilization
                utilization.append([x for x in x])
           
                x = user_api_instance.get_user_routingskills(user_id=id).entities
                if x:
                    acd_skills.append([x.name for x in x])
                else:
                    acd_skills.append(None) 
           
                x = user_api_instance.get_user_roles(user_id=id).roles
                if x:
                    roles.append([x.name for x in x])
                else:
                    for i in user_id:
                        roles.append(None)
                
                x = user_api_instance.get_user(user_id=id, expand= "locations")
                if x.locations !=[]:
                    for i in x.locations:
                        location_id= i.location_definition.id
                        location.append(locations_api_instance.get_location(location_id=location_id).name)
                else:
                    location.append(None)
        
            for i in range (1,len(user_id)+1):
                dicts[i] = [display_name[i-1], user_name[i-1], active[i-1], acd_skills[i-1],utilization[i-1], location[i-1], licenses[i-1], groups[i-1],roles[i-1], division[i-1]]         
                context= {'dicts': dicts, 'filter':filter, 'name':name, 'range': range(len(user_id))}
            return render(request, 'CloudApp/agent_role_report.html', context)
        

            
            
        
           
                
        
               
               
           

            


def download(request):
    Time = ('{:%Y-%b-%d}'.format(datetime.datetime.now()))
    Name = "Agent_Report_" + Time + ".csv"
    data = request.session['data']
    user_id = request.session['user_id']
    response = HttpResponse('')
    response['Content-Disposition'] = 'attachment; filename= {}'.format(Name)
    writer = csv.writer(response)
    writer.writerow([ 'Display Name', 'User Name', 'Division', 'Queue', 'Skills', 'Language Skills'])
    for d in range(len(user_id)):
            writer.writerow([data[0][d], data[1][d], data[2][d], data[3][d], data[4][d], data[5][d]])
    return response
    
    
    

    

    
        
