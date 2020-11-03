from django.shortcuts import render
from django.http import JsonResponse
# Create your views here.
import json
import joblib
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
from matplotlib import pyplot as plt
from .models import rankings
from django_pandas.io import read_frame
from rest_framework import generics, permissions
from rest_framework.response import Response
from knox.models import AuthToken
from .serializers import UserSerializer, RegisterSerializer

model = joblib.load('model1.pkl')



def scoreJson(request):
	print (request.body)
	qs = rankings.objects.all()
	df = read_frame(qs)


	df['weighted_points'] =  df['cur_year_avg_weighted'] + df['two_year_ago_weighted'] + df['three_year_ago_weighted']

	data = json.loads(request.body)
	x = data['Home'].capitalize()
	y = data['Away'].capitalize()

	home = df.loc[df['country_full'] == x]
	away = df.loc[df['country_full'] == y]

	frames = [home, away]
	result = pd.concat(frames)

	if x in df['country_full'].values and y in df['country_full'].values: 
		X_test3 = ['average_rank', 'rank_difference', 'point_difference', 'is_stake']
		row = pd.DataFrame(np.array([[np.nan, np.nan, np.nan, True]]), columns=X_test3)

		home_rank = result['rank'].iloc[0]
		home_points = result['weighted_points'].iloc[0]
		opp_rank = result['rank'].iloc[1]

		opp_points = result['weighted_points'].iloc[1]
		row['average_rank'] = (home_rank + opp_rank) / 2
		row['rank_difference'] = home_rank - opp_rank
		row['point_difference'] = home_points - opp_points

		home_win = model.predict_proba(row)
		print(home_win)
		#dataF = pd.DataFrame({'x':data})
		#print(dataF)
		#print(df)

		if home_win[0][0]>=0.45 and home_win[0][0]<=0.55:
			r="draw"
			print(r)
			return JsonResponse({'result':r})
		if home_win[0][0]>0.55:
			r = result['country_full'].iloc[1], "win with a probability of",home_win[0][0]
			print(r)
			return JsonResponse({'result':r})
		if home_win[0][1]>0.55:
			r = result['country_full'].iloc[0], "win with a probability of",home_win[0][1]
			print(r)
			return JsonResponse({'result':r})

	else:
		return JsonResponse({'result':'Error team not found!'})


# Register API
class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
        "user": UserSerializer(user, context=self.get_serializer_context()).data,
        "token": AuthToken.objects.create(user)[1]
        })

from django.contrib.auth import login

from rest_framework import permissions
from rest_framework.authtoken.serializers import AuthTokenSerializer
from knox.views import LoginView as KnoxLoginView

class LoginAPI(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return super(LoginAPI, self).post(request, format=None)
        