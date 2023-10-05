from django.shortcuts import render

from .models import *
from django.db.models import Q

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

import json
import csv
from collections import defaultdict
from itertools import combinations

def is_ajax(request):
    return request.headers.get("x-requested-with") == "XMLHttpRequest"

def index(request):
    return render(request, 'index.html')

#########################
# Catch all             #
#########################
def disclaimer(request):
    return render(request, 'ack.html')

def error(request):
    return render(request, 'error.html',{'message':var})

#########################
# Get table             #
#########################

def download_table(request, disease=None):
   
    (table,name) = generateTable(disease)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="'+name+"_"+disease+'.csv"'

    writer = csv.writer(response)
    #table.append((mim,names[mim],s,proteins[mim]))
    for row in table:
        writer.writerow([row[0], row[1], row[2], ','.join(row[3])])

    return response

def generateTable(disease):
    #store the nodes that were found, to check for double loops.
    direct_k_most = [(o2, float(s)) for o2,s in neighbourhood.objects.filter(omim1=disease).exclude(omim2=disease).order_by('-similarity').values_list('omim2', 'similarity')][:100]

    # we get the titles, for each disease
    all_names = dict(omim_details.objects.values_list('omim', 'title'))
    names = defaultdict()
    for (mim,s) in direct_k_most:
        names[mim] = all_names[mim]
    name = all_names[int(disease)]

    #we get the proteins for each disease
    proteins = defaultdict(list)
    for (mim,s) in direct_k_most:
        proteins[mim] = [i.uniprot_id for i in mimtoprot.objects.filter(omim__exact=mim)]

    #we fetch the similarities and percentiles.
    #sim = similarityScores.objects.get(omim1__exact = min(omim_A,omim_B), omim2__exact = max(omim_A,omim_B))

    #build the final tuple
    table = list()
    for (mim, s) in direct_k_most:
        table.append((mim,names[mim],s,proteins[mim]))
    return (table, name)


def getTable(request, disease=None):
    (table,name) = generateTable(disease)
    #return (direct_k_most, table)
    return render(request, 'table.html',{'table': table,'disease_name':name,'disease_omim':disease, 'num':len(table)})

#########################
# Result score          #
#########################
def ordinal(value):
    try:
        value = int(value)
    except ValueError:
        return value

    if value % 100//10 != 1:
        if value % 10 == 1:
            ordval = u"%d%s" % (value, "st")
        elif value % 10 == 2:
            ordval = u"%d%s" % (value, "nd")
        elif value % 10 == 3:
            ordval = u"%d%s" % (value, "rd")
        else:
            ordval = u"%d%s" % (value, "th")
    else:
        ordval = u"%d%s" % (value, "th")

    return ordval

def __getDiseaseDetails(omim):

    names = { 'A':'A - Anatomy', 'B':'B - Organisms', 'C':'C - Diseases', 'D':'D - Chemicals and Drugs', 'E':'E - Analytical, Diagnostic and Therapeutic Techniques and Equipment', 'F':'F - Psychiatry and Psychology', 'G':'G - Phenomena and Processes', 'H':'H - Disciplines and Occupations', 'I':'I - Anthropology, Education, Sociology and Social Phenomena', 'J':'J - Technology, Industry, Agriculture', 'K':'K - Humanities', 'L':'L - Information Science', 'M':'M - Named Groups', 'N':'N - Health Care', 'Z':'Z - Geographicals'} 

    mesh_unique = (list(set([(i.mesh_term,i.identifier,i.coordinates) for i in mesh.objects.filter(omim__exact=omim)])))

    mesh_terms = dict()
    found_terms = defaultdict(set)

    for i in mesh_unique:
        for coord in i[2].split(','):
            try:
                mesh_terms[names[coord[0]]]
            except:
                mesh_terms[names[coord[0]]] = list()

            if i[0] not in found_terms[names[coord[0]]]:
                #mesh_terms[names[coord[0]]].append((i[0], "http://www.nlm.nih.gov/cgi/mesh/2014/MB_cgi?mode=&term="+i[0].replace(' ', '+')+"&field=entry", i[1], i[2]))
                mesh_terms[names[coord[0]]].append((i[0], "https://meshb.nlm.nih.gov/#/record/ui?ui="+i[1], i[1], i[2]))
                found_terms[names[coord[0]]].add(i[0])
                
    for coord in mesh_terms:
        mesh_terms[coord] = sorted(mesh_terms[coord], key=lambda x:x[0])

    #get proteins
    proteins = [i.uniprot_id for i in mimtoprot.objects.filter(omim__exact=omim)]
    #get details
    details = get_object_or_404(omim_details, omim__exact=omim)
    #with prefix
    name_disease = details.title 
    return {'mesh':sorted(mesh_terms.items()), 'proteins':proteins,  'name_disease':name_disease, 'disease':details.omim}


def score(request, omim_A, omim_B):
    # this will hold the return variable.
    template_variables = defaultdict()

    # details for disease B
    details_A = __getDiseaseDetails(omim_A)
    template_variables['A_mesh'] = details_A['mesh']
    template_variables['A_proteins'] = details_A['proteins']
    template_variables['name_disease_A'] = details_A['name_disease']
    template_variables['disease_A'] = omim_A

    # details for disease B
    details_B = __getDiseaseDetails(omim_B)
    template_variables['B_mesh'] = details_B['mesh']
    template_variables['B_proteins'] = details_B['proteins']
    template_variables['name_disease_B'] = details_B['name_disease']
    template_variables['disease_B'] = omim_B

    # shared proteins and meshterms to highlight
    mesh_ids_A = set()
    for meshes in details_A["mesh"].values():
        for mesh in meshes:
            mesh_ids_A.add(mesh[1])

    mesh_ids_B = set()
    for meshes in details_B["mesh"].values():
        for mesh in meshes:
            mesh_ids_B.add(mesh[1])

    template_variables["shared_mesh"] = mesh_ids_A & mesh_ids_B
    template_variables["shared_proteins"] = (set(details_A['proteins'])
                                             & set(details_B['proteins']))

    # get the similarity of both diseases
    sim = similarityscores.objects.get(omim1__exact = int(min(omim_A,omim_B)), omim2__exact = int(max(omim_A,omim_B)))
    template_variables['similarity'] = sim.similarity
    template_variables['percentile'] = ordinal(round(sim.percentile * 100, 1))

    return render(request, 'score.html',template_variables)

#########################
# Explore neighbourhood #
#########################

def explore(request, disease):
    #this will hold the return variable.
    template_variables = defaultdict()

    details = get_object_or_404(omim_details, omim__exact=disease)
    (mim, name, prefix) = (details.omim, details.title, details.prefix)
    url = reverse('neighbourhood')
    url_fill = reverse('fillnetwork')

    #get the disease details.
    #details for disease B
    details = __getDiseaseDetails(disease)
    template_variables = {'chosen_disease_mim': mim, 'chosen_disease_name':name, 'URL':url, 'URL_fill': url_fill, 'omim': disease, 'mesh':details['mesh'], 'proteins': details['proteins']}

    return render(request, 'explore.html', template_variables)

def getNeighbourhood_ajax(request, disease=None, max_direct=10, max_indirect=5):
    #json prototype
    #nodes: [
            #{ data: { id: 'a', foo: 3, bar: 5, baz: 7 } },
            #{ data: { id: 'b', foo: 7, bar: 1, baz: 3 } },
            #], 
    #
    #edges: [
            #{ data: { id: 'ae', weight: 1, source: 'a', target: 'e' } },
            #{ data: { id: 'ab', weight: 3, source: 'a', target: 'b' } },
            #]
    #};

    #quick check to verify the limits are not exceeded.
    if int(max_direct) > 50:
        max_direct = 50
    if int(max_indirect) > 20:
        max_indirect = 20

    d3 = defaultdict(list)
    nodes = list()
    edges = list()


    #store the nodes that were found, to check for double loops.
    direct_k_most = [(o2, float(s),lca) for o2,s,lca in neighbourhood.objects.filter(omim1=disease).exclude(omim2=disease).order_by('-similarity').values_list('omim2', 'similarity','lca')][:int(max_direct)]

    # we get the titles, for each disease
    titles = dict(omim_details.objects.values_list('omim', 'title'))

    print(disease, int(disease) in titles)
    
    #append the pivot disease.
    nodes.append({'data': { 'id' :str(disease),'level': 230, 'colour': '#FFFFF', 'title': titles[int(disease)]},'classes':'centre'})
    d3['nodes'].append({'name':str(disease),'group':1})

    all_nodes = sorted([i[0] for i in direct_k_most])

    #set weights to store the mininmum and maximum weights. Easier than traversing the entire tree.
    min_sim = 1000
    max_sim = -1

    #store the found edges
    found_edges = set()

    for omim,score, lca in direct_k_most:
        nodes.append({'data': { 'id' : omim, 'level' : 160, 'title': titles[omim]}})

        source = str(min(str(disease),str(omim)))
        target = str(max(str(disease),str(omim)))
        edges.append({'data':{ 'id': str(disease)+"_"+str(omim), 'similarity': "{0:.2f}".format(float(score)), 'source': source, 'target': target, 'LCA':lca}})

        d3['nodes'].append({'name':str(omim), 'group':2})
        d3['links'].append({'source':source, 'target':target, 'value':float(score)})

        found_edges.add((source,target))
        #store teh similarities
        min_sim = min(min_sim,float(score)) 
        max_sim = max(max_sim,float(score)) 

    ##get the 50 most similar neighbours of each of the 50 original neighbours
    for (direct_neighbour,sim, lca) in direct_k_most:
        #fetch the neighbours
        second_k_most = [(o2, float(s),lca) for o2,s,lca in neighbourhood.objects.filter(omim1=direct_neighbour).exclude(omim2=direct_neighbour).order_by('-similarity').values_list('omim2', 'similarity','lca')][:int(max_indirect)]
        #add the current node
        all_nodes.extend(sorted([i[0] for i in direct_k_most]))
        index = 0
        for (omim, score, lca) in second_k_most:
            source = str(min(str(direct_neighbour),str(omim)))
            target = str(max(str(direct_neighbour),str(omim)))
            #check for double loops with the first level and double loops with the pivot disease.
            if (source,target) not in found_edges:

                nodes.append({'data': {'id' : str(omim), 'level' : 50 - ((index%2) * 40), 'title': titles[int(omim)]}})
                edges.append({'data':{'id': str(source) + "_"+target, 'similarity' : "{0:.2f}".format(float(score)), 'source': source, 'target': target, 'LCA':lca}})

                d3['nodes'].append({'name':str(omim),'group':3})
                d3['links'].append({'source':source, 'target':target, 'value':float(score)})

                found_edges.add((source,target))
                min_sim = min(min_sim,float(score)) 
                max_sim = max(max_sim,float(score)) 
            index += 1

    ##we normalise the values. This is to do with the javascript, were the linear mapping does not allow for variable limits, 
    #so we need everything between 0 and 1.
    for edge in edges:
        if max_sim == min_sim:
            edge['data']['colour'] = 1
        else:
            edge['data']['colour'] = (float(edge['data']['similarity']) - min_sim) / (max_sim - min_sim)
    ##set the json data to use
    final_set = defaultdict()
    #Just "round" the values to the closest decimal. It is just to make it look nicer.
    final_set['max_sim'] = float(max_sim)
    final_set['min_sim'] = float(min_sim)

    final_set['nodes'] = nodes
    final_set['edges'] = edges
    #return json.dumps(d3)
    return HttpResponse(json.dumps(final_set), content_type = "application/json")

def fillNetwork_ajax(request):
    #get the network
    network = json.loads(request.read())
    nodes = [i['data']['id'] for i in network['nodes']]
    edges = [(min(i['data']['source'],i['data']['target']),max(i['data']['source'],i['data']['target'])) for i in network['edges']]
    #set weights to store the mininmum and maximum weights. Easier than traversing the entire tree.
    min_sim = 1000
    max_sim = -1
    #look for all the edges that are not in the list of edges.
    for putative_edge in combinations(nodes, 2):
        if (min(putative_edge),max(putative_edge)) not in edges and min(putative_edge) != max(putative_edge):
            #here we fethc this from the database.
            sim = similarityscores.objects.get(omim1__exact = min(putative_edge), omim2__exact = max(putative_edge))
            network['edges'].append({'data' : {'id' : str(min(putative_edge))+"_"+str(max(putative_edge)) , 'similarity' : "{0:.2f}".format(float(sim.similarity)), 'source' : min(putative_edge), 'target' : max(putative_edge)}})
            #max similarity should not change, so we only fetch the min simialrity
            network['min_sim'] = min(float(network['min_sim']), float(sim.similarity))
            #add the found edges to avoid double edges.
            edges.append((min(putative_edge),max(putative_edge)))

    ##we normalise the values. This is to do with the javascript, were the linear mapping does not allow for variable limits, 
    #so we need everything between 0 and 1.
    for edge in network['edges']:
        if network['max_sim'] == network['min_sim']:
            edge['data']['colour'] = 1
        else:
            edge['data']['colour'] = (float(edge['data']['similarity']) - network['min_sim']) / (network['max_sim'] - network['min_sim'])

    return HttpResponse(json.dumps(network), content_type = "application/json")


#########################
# Disease details       #
#########################

def getDetails_ajax(request, omim):
    if is_ajax(request):
        json_data = defaultdict()
        #get details of disease A
        details = get_object_or_404(omim_details, omim__exact=omim)
        #get MeSH terms
        disease_mesh = set([i.mesh_term for i in mesh.objects.filter(omim__exact=omim)])
        #get proteins
        disease_proteins = [i.uniprot_id for i in mimtoprot.objects.filter(omim__exact=omim)]
        #create json data
        json_data = {'name':{'mim_no':details.omim, 'title':details.title, 'prefix':details.prefix}, 'proteins': disease_proteins, 'mesh': disease_mesh}
        return HttpResponse(json.dumps(json_data), content_type = "application/json")
    else:
        return render(request, 'error.html',{'message':''})



#########################
# Autocomplete          #
#########################

def get_entities(request):
    if is_ajax(request):
        data = ''
        # get data from the request.
        query = request.GET.get('term', '')
        # filter names
        results = omim_names.objects.filter(Q(label__icontains=query) | Q(value__icontains=query)).order_by('value')[:20]
        results = results.values_list('value', 'label')
        data = json.dumps([{"label": str(i[1]) + " ("+str(i[0]) + ")", "value": str(i[0])} for i in results])
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)


# Create your views here.
