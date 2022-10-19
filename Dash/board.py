from gettext import install

#importation des librairies
from dash import Dash
import dash
#import dash_core_components as dcc
from dash import dcc
#import dash_html_components as html
from dash import html
#from dash_extensions import Lottie
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import numpy as np

#permettra de gérer les cartes que l'on va créer, le style BOOTSTRAP peut être changer
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
#pour pouvoir uploader sur le web
server=app.server

#chargement du fichier
df=pd.read_csv('df_clean_deco.csv')

#Création d'un dictionnaire pour le filtre genre (dropdonw)
sex_dict=[{'label':html.Div(['Both'],style={'font-size':22}),'value':2},{'label':html.Div(['Women'],style={'font-size':22}),'value':0},{'label':html.Div(['Men'],style={'font-size':22}),'value':1}]

#regrouper selon idd du participant
#car il y a redondance des réponses par participant selon les critères
df_participant = df.groupby(['iid']).first()

#--------------fonctions
#fonction que renvoi un poucentage
def my_func(x):
    return x/np.sum(x)   

#Création d'un dictionnaire pour les professions des participants
dict_field = {'1.0' : 'Law', '2.0' : 'Math', '3.0' : 'Social Science, Psychologist ', '4.0' : 'Medical Science, Pharmaceuticals, and Bio Tech ', '5.0' : 'Engineering ', '6.0' :'English/Creative Writing/ Journalism ', '7.0' : 'History/Religion/Philosophy ', '8.0' : 'Business/Econ/Finance ', '9.0': 'Education, Academia' , '10.0' :'Biological Sciences/Chemistry/Physics','11.0':'Social Work','12.0': 'Undergrad/undecided','13.0' : 'Political Science/International Affairs', '14.0' : 'Film', '15.0' : 'Fine Arts/Arts Administration','16.0':'Languages','17.0':'Architecture','18.0':'Other' }
#fonction qui renvoi la profession en fonction selon sa postion
def topfield(df,n):
    #convertir pandas series en dataframe
    df = df.to_frame().reset_index()
    #Renommer les valeurs du dataframe
    df=df.replace({"index": dict_field})
    topc=df.iloc[n,0]
    return(topc)

#liste de l'ensemble des activités
activities=['yoga','sports','tvsports','exercise','dining','museums','art','hiking','gaming','clubbing','reading','tv','theater','movies','concerts','music','shopping']
#fonction qui renvoi un dataframe avec les indices de 0 à 10 
#et l'activité qui a eu la plus grande fréquence sur cet indice
def topactivity(df):
    #création du dataframe avec l'activité yoga
    yoga=df['yoga'].value_counts()
    new=pd.DataFrame(yoga)
    #création du data frame par activités et notation selon l'activité 
    for k in range(1,16) :
        new[activities[k]]=df[activities[k]].value_counts()
    #profil ligne
    activities_ligne=np.apply_along_axis(my_func,1,arr=new.values)
    #Création de dataframe avec les intitulés des colonnes correspondant aux activités
    df_activities_ligne=pd.DataFrame(activities_ligne,index=new.index,columns=new.columns)      
    #sélection du max pour les lignes correspondand aux notations 8,9,10
    selection=df_activities_ligne.idxmax(axis=1)
    #convertir pandas series en dataframe
    selection = selection.to_frame().reset_index()
    return(selection)

#Création d'un diagramme circulaire de l'âge 
#en fonction du choix de la partition adoptée (classes)
def pieage(df) :
    age_p=pd.DataFrame(df)
    #Nombre de participants ayant 22 ans ou moins
    n_18_22=age_p.iloc[0:5]['age'].sum()
    #Nombre de participants ayant entre 23 et 26 ans
    n_23_26=age_p.iloc[5:11]['age'].sum()
    #Nombre de participants ayant entre 27 et 30 ans
    n_27_30=age_p.iloc[11:17]['age'].sum()
    #Nombre de participants ayant entre 31 et 35 ans
    n_31_35=age_p.iloc[17:22]['age'].sum()
    #Nombre de participants ayant 36 ans ou plus
    n_36_42=age_p.iloc[22:27]['age'].sum()
    N=n_18_22+n_23_26+n_27_30+n_31_35+n_36_42
    #définir le dataframe pour les ages
    df_age=pd.DataFrame({'age': ['[18;23[', '[23;27[','[27,31[','[31;36[','[36,42]'],'nombre': [n_18_22,n_23_26,n_27_30,n_31_35,n_36_42],'frequence':[n_18_22/N,n_23_26/N,n_27_30/N,n_31_35/N,n_36_42/N]})
    #diagramme circulaire pour les âges
    fig_age = px.pie(df_age, values='nombre', names='age', title='Age of participants')
    return(fig_age)

#Création d'un diagramme en barres pour la variable date
def bardata(nb_sortie_rencontre):
    #tri ds valeurs par ordre croissant sur l'index
    nb_sortie_rencontre=nb_sortie_rencontre.sort_index(axis = 0, ascending = True)
    #convertir pandas series en dataframe
    nb_sortie_rencontre = nb_sortie_rencontre.to_frame().reset_index()
    #ajout d'une colonne contenant les fréquences
    nb_sortie_rencontre = nb_sortie_rencontre.assign(frequency=nb_sortie_rencontre.date/sum(nb_sortie_rencontre.date))
    #Création d'un dictionnaire pour les habitudes de sorties des participants concernant ce type d'événement
    dict = {'1.0' : 'Several times a week', '2.0' : 'Twice a week', '3.0' : 'Once a week', '4.0' : 'Twice a month', '5.0' : 'Once a month', '6.0' :'Several times a year', '7.0' : 'Almost never', 'Missing value' :'Other'}
    #Renommer les valeurs du dataframe
    nb_sortie_rencontre=nb_sortie_rencontre.replace({"index": dict})
    #bar plot date
    fig_date = px.bar(nb_sortie_rencontre, x="index", y="frequency", color="index", title="Frequency of participants going on dates")
    fig_date.update_layout(showlegend = False)
    return(fig_date)

#fonction qui renvoi le line plot de la moyenne de chaque attribut par vague 
#et aussi selon le sexe : k (k=2 : both)
#et match (n=1) ou non (n=0)
def scatter_attributes(n,k):
    #selection des matchs ou non match
    df_match=df.loc[(df.match==n)]
    #création d'un data frame avec les colonnes correspondant au futur scatter plot
    df_scatter=pd.DataFrame(columns=['wave','attributs','mean'])
    #liste des attributs
    attrib=['attr1_1','sinc1_1','intel1_1','fun1_1','amb1_1','shar1_1']
    for j in attrib:
        #sélection des vagues où le critère de notation est identique
        for i in [1,2,3,4,5,10,11,12,13,14,15,16,17]:
            #sélection des vagues et ergroupement par participant
            df_ind=(df_match.loc[df.wave==i]).groupby(['iid']).first()
            #si ensemble garder cette sélection
            if k==2 :
                df_mwi=df_ind
                #sinon refaire une sélection sur le sexe
            else :
                df_mwi=df_ind.loc[(df_ind.gender==k)]
            #calcul de la moyenne (j attribut) 
            moy=df_mwi[j].mean()
            #création des lignes dans le dataframe pour le scatter plot
            df_new_row=pd.DataFrame(np.array([[i,j,moy]]),columns=['wave','attributs','mean'])
            #insertion des lignes dans le dataframe pour le scatter plot
            df_scatter=pd.concat([df_scatter,df_new_row],ignore_index=True)
    #remtter les valeurs en numérique
    df_scatter[["wave", "mean"]] = df_scatter[["wave", "mean"]].apply(pd.to_numeric)
    #construction du scatter plot
    #fig_scatter=px.scatter(df_scatter, x='wave', y='mean',color='attributs',title='mean for each attributs for each wave')
    fig_scatter=px.line(df_scatter, x='wave', y='mean',color='attributs',title='mean for each attributs for each wave')
    return(fig_scatter)

#Définition d'un composant carte pour disposer d'une image de l'application
card_image=dbc.Card([
    dbc.CardImg(src="https://github.com/Skarbkit/M2_SISE-EasyDate/blob/9b038ce6099183765676100a72ef95eab9220cde/Dash/logo.png?raw=true",top=True, bottom=False,title="image by ???",alt="Sorry",style={'height':'30vh'})
    ],    
            style={'height':'100%'} #pour que les cartes sur une même ligne soient toutes de la même hauteur
        )

#Définition d'une carte qui créer un titre pour l'application
card_title=dbc.Card([
                    dbc.CardBody([
                            #écriture du texte dans le corps de la carte
                            #html.H2("EASY DATE",className="Card-title",style={'textAlign': 'center'}),
                            ])
                    ],
                    color="white", #choix de la couleur
                    inverse=True, #pour que le texte soit en blanc (sur fond noir)
                    outline=False, #True enlève la couleur de la carte
                    style={'height':'100%'},
                )

#Définition d'une carte pour filtrer selon le genre
card_filter_gender=dbc.Card([
                        dbc.CardBody([
                                html.H4("Select gender if you want",className="Card-text"),
                                #création de la barre de défilement pour sélectionner le sexe
                                #servira de input dans la fonction callback
                                dcc.Dropdown(id='sex-dropdown',options=sex_dict,value=2,style = {"color":"black"}),  
                            ]),
                        #pas de page de la carte
                        dbc.CardFooter(dcc.RadioItems(id='match-items',
                        options=[{"label": 
                        html.Div(['Match'], style={'font-size': 22}),"value": 1},
                                {"label": html.Div(['No Match'], style={'font-size': 22}),"value": 0}],value=1),),
                        ],
                        color="secondary", #choix de la couleur
                        inverse=True,
                        outline=False, #True enlève la couleur de la carte
                        style={'height':'100%'},
                        className="w-75",
                    )

#Définition d'une carte pour la variable fun et succès des matchs
card_fun_success=dbc.Card([
                        dbc.CardBody([
                                html.H4("KPI mean fun_o success",className="Card-text"),
                                #affichage de l'output fun_o_succes en fonction du genre
                                html.P('',style={'height':'3vh'}),
                                html.H2(id='fun_o_success')
                            ]),
                        ],
                        color="success",
                        inverse=True,
                        outline=False,
                        style={'textAlign':'center','height':'100%'},
                        )  

##Définition d'une carte pour la variable fun et échec des matchs
card_fun_no_success=dbc.Card([
                        dbc.CardBody([
                                html.H4("KPI mean fun_o no success",className="Card-text"),
                                #créer un espace entre le texte et l'indicateur
                                html.P('',style={'height':'3vh'},),
                                #affichage de l'output fun_o_no_succes en fonction du genre
                                html.H2(id='fun_o_no_success')
                            ])
                        ],
                        color="danger",
                        inverse=True,
                        outline=False,
                        style={'textAlign':'center','height':'100%'},
                        ) 

#Définition d'une carte pour les professions
card_top_career=dbc.Card([
                        dbc.CardBody([
                                html.H4("Top 3 : career",className="Card-text"),
                                #affichage de la profession la plus représentée n°1
                                #output dépendra de genre
                                html.H4(id='top_career1'),
                                #affichage de la profession la plus représentée n°2
                                html.H4(id='top_career2'),
                                #affichage de la profession la plus représentée n°3
                                html.H4(id='top_career3')
                            ])
                        ],
                        color="warning",
                        inverse=True,
                        outline=False,
                        #style={'textAlign':'center'}
                        style={'textAlign':'center','height':'100%'}
                        ) 

#Définition d'une carte pour les activités
card_top_activities=dbc.Card([
                        dbc.CardBody([
                                html.H4("Top 3 : activities",className="Card-text"),
                                #affichage de l'activité la plus représentée pour l'indice le plus élevé
                                #l'output dépendra de genre
                                html.H4(id='top_act1'),
                                html.H4(id='top_act2'),
                                html.H4(id='top_act3')
                            ])
                        ],
                        color="info",
                        inverse=True,
                        outline=False,
                        style={'textAlign':'center','height':'100%'},
                        ) 

#Définition d'une carte pour le diagramme circulaire de la variable âge
card_pie=dbc.Card([
                    dbc.CardBody([
                        #affichage du diagramme circulaire âge (output) 
                        #en fonction du genre (input)
                        dcc.Graph(id='pie_chart',figure={})
                        ])
                    ],
                    color="light",
                    inverse=False,
                    outline=False,
                    #style={'height':'120vh'},
                    ) 

#Définition d'une carte pour le diagramme en tuyaux d'orgues pour la variable date
card_bar=dbc.Card([
                    dbc.CardBody([
                        #affichage du diagramme en barres de la variable date (output) 
                        #en fonction du genre (input)
                        dcc.Graph(id='bar_chart',figure={})
                        ])
                    ],
                    color="light",
                    inverse=False,
                    outline=False,
                    #style={'height':'120vh'},
                    ) 

card_scatter=dbc.Card([
                    dbc.CardBody([
                        #affichage du diagramme en barres de la variable date (output) 
                        #en fonction du genre (input)
                        dcc.Graph(id='scatter_chart',figure={})
                        ])
                    ],
                    color="light",
                    inverse=False,
                    outline=False,
                    #style={'height':'120vh'},
                    ) 

#Gestion de l'application avec les différentes cartes
app.layout = dbc.Container(
    #on indique le nombre de lignes et de colonnes 
    #permet d'avoir la structure de la page qui sera affichée
    [   dbc.Row(
            [
                dbc.Col(card_image,width=6),
                dbc.Col(card_filter_gender,width=3),
            ],
            justify="end",
        ),
        dbc.Row(
            [   
                dbc.Col(card_fun_success,width=3),
                dbc.Col(card_fun_no_success,width=3),
                dbc.Col(card_top_career,width=3),
                dbc.Col(card_top_activities,width=3)
            ],
        ),
        dbc.Row([],style={'height':'3vh'},),
        dbc.Row(
            [
                dbc.Col(card_pie,width=3),
                dbc.Col(card_bar, width=4),
                dbc.Col(card_scatter,width=5)
            ],
        ),
    ],
    fluid=True, #pour que l'ensembles des cartes ne soient pas "figées"
)

#------------------------------------------callback functions
@app.callback(
    #les différentes sorties qui seront répercutées dans les cartes, les fonctions
    Output(component_id='fun_o_success',component_property='children'),
    Output(component_id='fun_o_no_success',component_property='children'),
    Output(component_id='top_career1',component_property='children'),
    Output(component_id='top_career2',component_property='children'),
    Output(component_id='top_career3',component_property='children'),
    Output(component_id='top_act1',component_property='children'),
    Output(component_id='top_act2',component_property='children'),
    Output(component_id='top_act3',component_property='children'),
    Output(component_id='pie_chart',component_property='figure'),
    Output(component_id='bar_chart',component_property='figure'),
    #la variable qui fera évoler les outputs (indices, graphiques,...) ci-dessus
    Input(component_id='sex-dropdown',component_property='value')
)
def update_output(choix):
#retour des outputs selon le choix du genre
    #pour l'ensemble des participants
    if choix==2:
        #moyenne fun_o et success match
        mean_fun_success=round(df.loc[(df.match==1)].fun_o.mean(),3)
        #moyenne des fun_o et no success match
        mean_fun_no_success=round(df.loc[(df.match==0)].fun_o.mean(),3)
        #compte le nombre de fois où chaque profession apparait
        new_field=df_participant.field_cd.value_counts()
        #renvoi la profession la plus représentée n°1
        top_field0=topfield(new_field,0)
        #celle en n°2
        top_field1=topfield(new_field,1)
        #celle en n°3
        top_field2=topfield(new_field,2)
        #renvoi l'activité la plus représentée pour la valeur "10"
        top_act0=topactivity(df_participant).iloc[8,1]
        #idem pour la veleur "9"
        top_act1=topactivity(df_participant).iloc[9,1]
        #idem pour la valeur "8"
        top_act2=topactivity(df_participant).iloc[7,1]
        #renvoi le nmbre de participants selon l'âge par ordre croissant
        age_participant=(df_participant.age.value_counts()).sort_index(axis = 0, ascending = True)
        #renvoi le diagramme circulaire des âges regroupés en classe
        piechart_age=pieage(age_participant)
        #compte le nombre de participants selon les différentes modalités de la variable date
        df_date=df_participant.date.value_counts()
        #renvoi le diagramme en barres selon la variable date
        barchart_date=bardata(df_date) 
    #même renvoi et fonctionnalité pour les hommes
    elif choix==1 :
        mean_fun_success=round(df.loc[(df.match==1)&(df.gender==1)].fun_o.mean(),3)
        mean_fun_no_success=round(df.loc[(df.match==0)&(df.gender==1)].fun_o.mean(),3)
        field_m=df_participant.loc[(df.gender==1)].field_cd.value_counts()
        top_field0=topfield(field_m,0)
        top_field1=topfield(field_m,1)
        top_field2=topfield(field_m,2)
        #tri du fichier participant selon le genre homme
        df_male=df_participant.loc[(df.gender==1)]
        top_act0=topactivity(df_male).iloc[9,1]
        top_act1=topactivity(df_male).iloc[8,1]
        top_act2=topactivity(df_male).iloc[6,1]
        age_male=(df_male.age.value_counts()).sort_index(axis = 0, ascending = True)
        piechart_age=pieage(age_male)
        date_male=df_participant.loc[(df.gender==1)].date.value_counts()
        barchart_date=bardata(date_male)
    #même renvoi pour les femmes
    elif choix==0 :
        mean_fun_success=round(df.loc[(df.match==1)&(df.gender==0)].fun_o.mean(),3)
        mean_fun_no_success=round(df.loc[(df.match==0)&(df.gender==0)].fun_o.mean(),3)
        field_w=df_participant.loc[(df.gender==0)].field_cd.value_counts()
        top_field0=topfield(field_w,0)
        top_field1=topfield(field_w,1)
        top_field2=topfield(field_w,2)
        #tri du fichier participant selon le genre femme
        df_female=df_participant.loc[(df.gender==0)]
        top_act0=topactivity(df_female).iloc[9,1]
        top_act1=topactivity(df_female).iloc[7,1]
        top_act2=topactivity(df_female).iloc[4,1]
        age_female=(df_female.age.value_counts()).sort_index(axis = 0, ascending = True)
        piechart_age=pieage(age_female)
        date_female=df_participant.loc[(df.gender==0)].date.value_counts()
        barchart_date=bardata(date_female)
    #renvoi de tous les outputs (quiseront intégrés dans les différentes cartes)
    return mean_fun_success,mean_fun_no_success,top_field0,top_field1,top_field2,top_act0,top_act1,top_act2,piechart_age,barchart_date

@app.callback(
    Output(component_id='scatter_chart',component_property='figure'),
    Input(component_id='match-items',component_property='value'),
    Input(component_id='sex-dropdown',component_property='value')
)
def update_output(decision,choix):
    figscatter=scatter_attributes(decision,choix)
    return figscatter

if __name__ == "__main__":
    app.run_server(debug=True)

