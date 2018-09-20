from __future__ import division

import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as st
import statsmodels.api as sm

import sys
import os
from random import randint
from random import shuffle
import math
import collections
import evaluation_measures


'''
=============================================
FUNCTII AUXILIARE
'''

class MariaClust:

	def __init__(self, no_clusters, no_bins, expand_factor, cluster_distance, no_dims):
		
		self.no_clusters = no_clusters 
		self.no_bins = no_bins
		self.expand_factor = expand_factor # expantion factor how much a cluster can expand based on the number of neighbours -- factorul cu care inmultesc closest mean (cat de mult se poate extinde un cluster pe baza vecinilor)
		self.cluster_distance = cluster_distance
		self.no_dims = no_dims

		self.id_cluster = -1
		self.pixels_partition = list()
		self.pdf = list()

		'''
		how you compute the dinstance between clusters:
		1 = centroid linkage
		2 = average linkage
		3 = single linkage
		4 = average linkage ponderat
		'''

	def agglomerative_clustering2(self, partitions, final_no_clusters, cluster_distance):
		'''
		Clusterizare ierarhica aglomerativa pornind de la niste clustere (partitii) deja create
		Fiecare partitie este reprezentata de catre centroidul ei
		Identificatorii partitiilor sunt pastrati in lista intermediary_centroids, iar clusterele cu punctele asociate sunt pastrate in dictionarul cluster_points.
		cluster_points => cheile sunt identificatorii partitiilor (centroizii lor), iar valorile sunt punctele asociate
		Criteriul de unire a doua clustere variaza'''

		no_agg_clusters = len(partitions)
		intermediary_centroids = list()
		#intermediary_centroids este de o lista cu identificatorii clusterelor
		
		'''
		clusterele sunt mentiunte in cluster_points
		id-ul unui cluster este centroidul lui
		'''

		#cluster_points = collections.defaultdict(list)

		cluster_points = dict()

		print("len partitions "+str(len(partitions)))

		for k in partitions:
			centroid_partition = self.centroid(partitions[k])
			idx_dict = list()
			for dim in range(no_dims):
				idx_dict.append(centroid_partition[dim])
			cluster_points[tuple(idx_dict)] = []
			intermediary_centroids.append(centroid_partition)
		
		for k in partitions:
			centroid_partition = self.centroid(partitions[k])
			idx_dict = list()
			for dim in range(no_dims):
				idx_dict.append(centroid_partition[dim])
			for pixel in partitions[k]:
				cluster_points[tuple(idx_dict)].append(pixel)

		#print cluster_points

		while(no_agg_clusters > final_no_clusters):
			uneste_a_idx = 0
			uneste_b_idx = 0
			minDist = 99999
			minDistancesWeights = list()
			mdw_uneste_a_idx = list()
			mdw_uneste_b_idx = list()
			for q in range(len(intermediary_centroids)):
				for p in range(q+1, len(intermediary_centroids)):
					idx_dict_q = list()
					idx_dict_p = list()
					for dim in range(self.no_dims):
						idx_dict_q.append(intermediary_centroids[q][dim])
						idx_dict_p.append(intermediary_centroids[p][dim])

					centroid_q = self.centroid(cluster_points[tuple(idx_dict_q)])
					centroid_p = self.centroid(cluster_points[tuple(idx_dict_p)])
					if(centroid_q!=centroid_p):
						# calculate_smallest_pairwise pentru jain si spiral
						if(cluster_distance==1):
							dist = self.calculate_centroid(cluster_points[tuple(idx_dict_q)], cluster_points[tuple(idx_dict_p)])					
						elif(cluster_distance==2):
							dist = self.calculate_average_pairwise(cluster_points[tuple(idx_dict_q)], cluster_points[tuple(idx_dict_p)])
						elif(cluster_distance==3):
							dist = self.calculate_smallest_pairwise(cluster_points[tuple(idx_dict_q)], cluster_points[tuple(idx_dict_p)])
						elif(cluster_distance==4):
							dist = self.calculate_weighted_average_pairwise(cluster_points[tuple(idx_dict_q)], cluster_points[tuple(idx_dict_p)])
						else:
							dist = self.calculate_centroid(cluster_points[tuple(idx_dict_q)], cluster_points[tuple(idx_dict_p)])
					
					if(dist<minDist):
						minDist = dist
						uneste_a_idx = q
						uneste_b_idx = p
						
			helperCluster = list()

			idx_uneste_a = list()
			idx_uneste_b = list()

			for dim in range(self.no_dims):
				idx_uneste_a.append(intermediary_centroids[uneste_a_idx][dim])
				idx_uneste_b.append(intermediary_centroids[uneste_b_idx][dim])

			for cluster_point in cluster_points[tuple(idx_uneste_a)]:
				helperCluster.append(cluster_point)
			
			for cluster_point in cluster_points[tuple(idx_uneste_b)]:
				helperCluster.append(cluster_point)

			
			newCluster = self.centroid(helperCluster)

			
			del cluster_points[tuple(idx_uneste_a)]
			del cluster_points[tuple(idx_uneste_b)]

			idx_cluster = list()
			for dim in range(self.no_dims):
				idx_cluster.append(newCluster[dim])

			cluster_points[tuple(idx_cluster)] = []
			for pointHelper in helperCluster:
				cluster_points[tuple(idx_cluster)].append(pointHelper)

			
			value_a = intermediary_centroids[uneste_a_idx]
			value_b = intermediary_centroids[uneste_b_idx]


			for cluster_point in cluster_points[tuple(idx_cluster)]:
				if(cluster_point in intermediary_centroids):
					intermediary_centroids = list(filter(lambda a: a != cluster_point, intermediary_centroids))
			
			if(value_a in intermediary_centroids):
				intermediary_centroids = list(filter(lambda a: a != value_a, intermediary_centroids))

			if(value_b in intermediary_centroids):
				intermediary_centroids = list(filter(lambda a: a != value_b, intermediary_centroids))


			'''
			if row is a list, then don't forget that deleting an element of a list will move all following elements back one place to fill the gap
			https://stackoverflow.com/questions/3392677/python-list-assignment-index-out-of-range
			---de ce am scazut 1
			'''

			intermediary_centroids.append(newCluster)	
			no_agg_clusters = len(cluster_points)
			

		return intermediary_centroids, cluster_points

	def compute_pdf_kde_scipy(self, dataset_xy, each_dimension_values):
		'''
		Calculeaza functia probabilitate de densitate si intoarce valorile ei pentru
		punctele din dataset_xy
		'''
		stacking_list = list()
		for dim_id in each_dimension_values:
			stacking_list.append(each_dimension_values[dim_id])
		values = np.vstack(stacking_list)
		kernel = st.gaussian_kde(values) #bw_method=
		pdf = kernel.evaluate(values)

		scott_fact = kernel.scotts_factor()
		print("who is scott? "+str(scott_fact))
		return pdf

	def compute_pdf_kde(self, dataset_xy, each_dimension_values):
		values_list = list()
		for dim_id in each_dimension_values:
			stacking_list = list()
			for point in each_dimension_values[dim_id]:
				stacking_list.append([point])
			#print(np.shape(stacking_list))
			values_list.append(stacking_list)
		#print(np.shape(values_list))
		dens_u = sm.nonparametric.KDEMultivariate(data=values_list, var_type='cc', bw='normal_reference')

		pdf = dens_u.pdf()

		return pdf


	def evaluate_pdf_kde(self, dataset_xy, each_dimension_values):
		'''
		Functioneaza doar pentru doua dimensiuni
		Genereaza graficul in nuante de albastru pentru functia probabilitate de densitate
		calculata pentru dataset_xy
		'''
		x = list()
		y = list()

		x = each_dimension_values[0]
		y = each_dimension_values[1]

		xmin = min(x)-2
		xmax = max(x)+2

		ymin = min(y)-2
		ymax = max(y)+2

		# Peform the kernel density estimate
		xx, yy = np.mgrid[xmin:xmax:100j, ymin:ymax:100j]
		positions = np.vstack([xx.ravel(), yy.ravel()])
		values = np.vstack([x, y])
		kernel = st.gaussian_kde(values) #bw_method=

		scott_fact = kernel.scotts_factor()
		print("who is scott eval? "+str(scott_fact))

		f = np.reshape(kernel(positions).T, xx.shape)
		return (f,xmin, xmax, ymin, ymax, xx, yy)


	def random_color_scaled(self):
		b = randint(0, 255)
		g = randint(0, 255)
		r = randint(0, 255)
		return [round(b/255,2), round(g/255,2), round(r/255,2)]

	#Distanta Euclidiana dintre doua puncte 2d
	def DistFunc(self, x, y):

		sum_powers = 0
		for dim in range(self.no_dims):
			sum_powers = math.pow(x[dim]-y[dim], 2) + sum_powers
		return math.sqrt(sum_powers)

	def centroid(self, pixels):
		
		sum_each_dim = {}
		for dim in range(self.no_dims):
			sum_each_dim[dim] = 0

		for pixel in pixels:
			for dim in range(self.no_dims):
				sum_each_dim[dim] = sum_each_dim[dim] + pixel[dim]
		
		centroid_coords = list()
		for sum_id in sum_each_dim:
			centroid_coords.append(round(sum_each_dim[sum_id]/len(pixels), 2))

		centroid_coords = tuple(centroid_coords)

		return centroid_coords

		
	def outliers_iqr(self, ys):
		'''
		Determina outlierii cu metoda inter-quartilelor
		'''
		quartile_1, quartile_3 = np.percentile(ys, [25, 75])
		iqr = quartile_3 - quartile_1
		lower_bound = quartile_1 - (iqr * 1.5)
		upper_bound = quartile_3 + (iqr * 1.5)
		outliers_iqr = list()
		for idx in range(len(ys)):
			if ys[idx] < lower_bound:
				outliers_iqr.append(idx)
		return outliers_iqr

	def get_closest_mean(self):
		'''
		Media distantelor celor mai apropiati k vecini pentru fiecare punct in parte

		'''

		just_pdfs = [point[self.no_dims+1] for point in self.pixels_partition]
		just_pdfs = list(set(just_pdfs))

		mean_pdf = sum(just_pdfs)/len(just_pdfs)
		k=int(math.ceil(0.1*len(self.pixels_partition)))
		distances = list()

		for point in self.pixels_partition:
			deja_parsati = list()
			if(point[no_dims+1] > mean_pdf):
				while(k>0):
					neigh_id = 0
					minDist = 99999
					for id_point_k in range(len(self.pixels_partition)):
						point_k = self.pixels_partition[id_point_k]
						if(point_k not in deja_parsati):
							dist = self.DistFunc(point, point_k)
							if(dist < minDist and dist > 0):
								minDist = dist
								neigh_id = id_point_k
					distances.append(minDist)
					neigh = self.pixels_partition[neigh_id]
					deja_parsati.append(neigh)
					k=k-1
		distances = list(set(distances))
		return sum(distances)/len(distances)

	def get_closestk_neigh(self, point, id_point):
		'''
		Cei mai apropiati v vecini fata de un punct.
		Numarul v nu e constant, pentru fiecare punct ma extind cat de mult pot, adica
		atata timp cat distanta dintre punct si urmatorul vecin este mai mica decat
		expand_factor * closest_mean (closest_mean este calculata de functia anterioara)
		'''
		
		neigh_ids = list()
		distances = list()
		deja_parsati = list()
		pot_continua = 1
		closest_mean = self.get_closest_mean()
		while(pot_continua==1):
			minDist = 99999
			neigh_id = 0
			for id_point_k in range(len(self.pixels_partition)):
				point_k = self.pixels_partition[id_point_k]
				if(point_k not in deja_parsati):
					dist = self.DistFunc(point, point_k)
					if(dist < minDist and dist > 0):
						minDist = dist
						neigh_id = id_point_k
			

			if(minDist <= expand_factor*closest_mean):
				neigh = self.pixels_partition[neigh_id]
				neigh_ids.append([neigh_id, neigh])
				distances.append(minDist)
				
				deja_parsati.append(neigh)
			else:
				pot_continua = 0
			
		neigh_ids.sort(key=lambda x: x[1])

		neigh_ids_final = [n_id[0] for n_id in neigh_ids]

		return neigh_ids_final


	def expand_knn(self, point_id):
		'''
		Extind clusterul curent 
		Iau cei mai apropiati v vecini ai punctului curent
		Ii adaug in cluster
		Iau cei mai apropiati v vecini ai celor v vecini
		Cand toate punctele sunt parcurse (toti vecinii au fost parcursi) ma opresc si incep cluster nou
		'''

		point = self.pixels_partition[point_id]
		neigh_ids = self.get_closestk_neigh(point, point_id)
		
		if(len(neigh_ids)>0):
			self.pixels_partition[point_id][self.no_dims] = self.id_cluster
			self.pixels_partition[point_id][self.no_dims+2] = 1
			for neigh_id in neigh_ids:
				
				if(self.pixels_partition[neigh_id][self.no_dims+2]==-1):
					self.expand_knn(neigh_id)
		else:
			self.pixels_partition[point_id][self.no_dims] = -1
			self.pixels_partition[point_id][self.no_dims+2] = 1
			

	def calculate_weighted_average_pairwise(self, cluster1, cluster2):
		
		'''
		Average link method ponderat - functia calculate_average_pairwise
			- calculeaza media ponderata a punctelor dintre doua clustere candidat
			- ponderile sunt densitatile punctelor estimate cu metoda kernel density estimation
		'''

		average_pairwise = 0
		sum_pairwise = 0
		sum_ponderi = 0

		for pixel1 in cluster1:
			for pixel2 in cluster2:
				distBetween = self.DistFunc(pixel1, pixel2)
				
				sum_pairwise = sum_pairwise + abs(pixel1[self.no_dims+1]-pixel2[self.no_dims+1])*distBetween
				sum_ponderi = sum_ponderi + abs(pixel1[self.no_dims+1]-pixel2[self.no_dims+1])

		average_pairwise = sum_pairwise/sum_ponderi
		return average_pairwise


	def calculate_average_pairwise(self, cluster1, cluster2):

		average_pairwise = 0
		sum_pairwise = 0
		nr = 0

		for pixel1 in cluster1:
			for pixel2 in cluster2:
				distBetween = self.DistFunc(pixel1, pixel2)
				sum_pairwise = sum_pairwise + distBetween
				nr = nr + 1

		average_pairwise = sum_pairwise/nr
		return average_pairwise

	def calculate_smallest_pairwise(self, cluster1, cluster2):

		min_pairwise = 999999
		for pixel1 in cluster1:
			for pixel2 in cluster2:
				if(pixel1!=pixel2):
					distBetween = self.DistFunc(pixel1, pixel2)
					if(distBetween < min_pairwise):
						min_pairwise = distBetween
		return min_pairwise


	def calculate_centroid(self, cluster1, cluster2):
		centroid1 = self.centroid(cluster1)
		centroid2 = self.centroid(cluster2)

		dist = self.DistFunc(centroid1, centroid2)

		return dist

	def split_partitions(self, partition_dict):

		print("Expand factor "+str(self.expand_factor))
		noise = list()
		no_clusters_partition = 1
		part_id=0
		final_partitions = collections.defaultdict(list)

		for k in partition_dict:
			self.pixels_partition = partition_dict[k]

			self.id_cluster = -1

			for pixel_id in range(len(self.pixels_partition)):
				pixel = self.pixels_partition[pixel_id]
				
				if(self.pixels_partition[pixel_id][self.no_dims]==-1):
					self.id_cluster = self.id_cluster + 1
					no_clusters_partition = no_clusters_partition + 1
					self.pixels_partition[pixel_id][self.no_dims+2] = 1
					self.pixels_partition[pixel_id][self.no_dims] = self.id_cluster
					neigh_ids = self.get_closestk_neigh(pixel, pixel_id)
					
					for neigh_id in neigh_ids:
						if(self.pixels_partition[neigh_id][self.no_dims]==-1):
							self.pixels_partition[neigh_id][self.no_dims+2]=1
							self.pixels_partition[neigh_id][self.no_dims]=self.id_cluster
							self.expand_knn(neigh_id)
						
			inner_partitions = collections.defaultdict(list)
			inner_partitions_filtered = collections.defaultdict(list)
			part_id_inner = 0

			for i in range(no_clusters_partition):
				for pixel in self.pixels_partition:
					if(pixel[self.no_dims]==i):
						inner_partitions[part_id_inner].append(pixel)
				part_id_inner = part_id_inner+1
			#adaug si zgomotul
			for pixel in self.pixels_partition:
				if(pixel[self.no_dims]==-1):
					inner_partitions[part_id_inner].append(pixel)
					part_id_inner = part_id_inner+1
					

			#filter partitions - le elimin pe cele care contin un singur punct
			keys_to_delete = list()
			for k in inner_partitions:
				if(len(inner_partitions[k])<=1):
					keys_to_delete.append(k)
					#salvam aceste puncte si le reasignam la sfarsit celui mai apropiat cluster
					if(len(inner_partitions[k])>0):
						for pinner in inner_partitions[k]:
							noise.append(pinner)
			for k in keys_to_delete:
				del inner_partitions[k]

			part_id_filtered = 0
			for part_id_k in inner_partitions:
				inner_partitions_filtered[part_id_filtered] = inner_partitions[part_id_k]
				part_id_filtered = part_id_filtered + 1


			for part_id_inner in inner_partitions_filtered:
				final_partitions[part_id] = inner_partitions_filtered[part_id_inner]
				part_id = part_id + 1

		return (final_partitions, noise)


	def evaluate_cluster(self, clase_points, cluster_points):
		
		evaluation_dict = {}
		point2cluster = {}
		point2class = {}

		idx = 0
		for elem in clase_points:
			evaluation_dict[idx] = {}
			for points in clase_points[elem]:
				point2class[points] = idx
			idx += 1

		idx = 0
		for elem in cluster_points:
			for point in cluster_points[elem]:
				index_dict = list()
				for dim in range(self.no_dims):
					index_dict.append(point[dim])
				point2cluster[tuple(index_dict)] = idx
			for c in evaluation_dict:
				evaluation_dict[c][idx] = 0
			idx += 1

		'''for point in point2class:		
			if point2cluster.get(point, -1) == -1:
				print("punct pierdut dupa clustering:", point)'''

		for point in point2cluster:
			evaluation_dict[point2class[point]][point2cluster[point]] += 1
				

		print('Purity:  ', evaluation_measures.purity(evaluation_dict))
		print('Entropy: ', evaluation_measures.entropy(evaluation_dict)) # perfect results have entropy == 0
		print('RI       ', evaluation_measures.rand_index(evaluation_dict))
		print('ARI      ', evaluation_measures.adj_rand_index(evaluation_dict))

	def cluster_dataset(self, dataset_xy, dataset_xy_validate, each_dimension_values, clase_points):

		partition_dict = collections.defaultdict(list)			

		self.pdf = self.compute_pdf_kde(dataset_xy, each_dimension_values) #calculez functia densitate probabilitate utilizand kde

		#detectie si eliminare outlieri

		outliers_iqr_pdf = self.outliers_iqr(self.pdf)
		print("We identified "+str(len(outliers_iqr_pdf))+" outliers from "+str(len(dataset_xy))+" points")
		'''
		print("The outliers are:")
		for outlier_id in outliers_iqr_pdf:
			print(dataset_xy[outlier_id])'''
		print("======================================")

		dataset_xy_aux = list()
		each_dimension_values_aux = collections.defaultdict(list)

		#refac dataset_xy, x si y

		dataset_xy = [dataset_xy[q] for q in range(len(dataset_xy)) if q not in outliers_iqr_pdf]
		dataset_xy_validate = [dataset_xy[q] for q in range(len(dataset_xy))]
		for dim in range(no_dims):
			each_dimension_values[dim] = [dataset_xy[q][dim] for q in range(len(dataset_xy))]

		'''for q in range(len(dataset_xy)):
			if(q not in outliers_iqr_pdf):
				dataset_xy_aux.append(dataset_xy[q])
				for dim in range(no_dims):
					each_dimension_values_aux[dim].append(dataset_xy[q][dim])

		dataset_xy = dataset_xy_aux
		each_dimension_values = each_dimension_values_aux'''

		#recalculez pdf, ca altfel se produc erori

		self.pdf = self.compute_pdf_kde(dataset_xy, each_dimension_values) #calculez functia densitate probabilitate din nou
		if(self.no_dims==2):
			#coturul cu albastru este plotat doar pentru 2 dimensiuni
			f,xmin, xmax, ymin, ymax, xx, yy = self.evaluate_pdf_kde(dataset_xy, each_dimension_values) #pentru afisare zone dense albastre
			plt.contourf(xx, yy, f, cmap='Blues') #pentru afisare zone dense albastre
			
		
		'''
		Impart punctele din setul de date in n bin-uri in functie de densitatea probabilitatii. 
		Numarul de bin-uri este numarul de clustere - 1
		'''

		pixels_per_bin, bins = np.histogram(self.pdf, bins=self.no_bins)

		#afisare bin-uri rezultate si creare partitii - un bin = o partitie
		for idx_bin in range( (len(bins)-1) ):
			culoare = self.random_color_scaled()
			for idx_point in range(len(dataset_xy)):
				if(self.pdf[idx_point]>=bins[idx_bin] and self.pdf[idx_point]<=bins[idx_bin+1]):
					element_to_append = list()
					for dim in range(self.no_dims):
						element_to_append.append(dataset_xy[idx_point][dim])
					element_to_append.append(-1) #clusterul nearest neighbour din care face parte punctul
					element_to_append.append(self.pdf[idx_point])
					element_to_append.append(-1) #daca punctul e deja parsta nearest neighbour
					element_to_append.append(idx_point) 
					element_to_append.append(dataset_xy_validate[idx_point])
					partition_dict[idx_bin].append(element_to_append)
					#scatter doar pentru 2 sau 3 dimensiuni
					if(self.no_dims == 2):
						plt.scatter(dataset_xy[idx_point][0], dataset_xy[idx_point][1], color=culoare)
					elif(self.no_dims == 3):
						plt.scatter(dataset_xy[idx_point][0], dataset_xy[idx_point][1], dataset_xy[idx_point][2], color=culoare)
		if(self.no_dims == 2 or self.no_dims == 3):
			plt.show()


		'''
		Pasul anterior atribuie zonele care au aceeasi densitate aceluiasi cluster, chiar daca aceste zone se afla la distanta mare una fata de cealalta.
		De aceea aplic un algoritm similar DBSCAN pentru a determina cat de mult se extinde o zona de densitate, si astfel partitionez zonele care se afla la distanta mare una fata de alta.
		Unesc partitiile rezultate in urma separarii utilizand clusterizarea ierarhica aglomerativa modificata (utilizeaza media ponderata pentru unirea clusterelor)
		'''
		
		final_partitions, noise = self.split_partitions(partition_dict) #functie care scindeaza partitiile
		
		if(self.no_dims==2):
			for k in final_partitions:
				color = self.random_color_scaled()
				for pixel in final_partitions[k]:
					plt.scatter(pixel[0], pixel[1], color=color)

			plt.show()


		intermediary_centroids, cluster_points = self.agglomerative_clustering2(final_partitions, self.no_clusters, self.cluster_distance) #paramateri: partitiile rezultate, numarul de clustere
		
		#reasignez zgomotul clasei cu cel mai apropiat vecin
		for noise_point in noise:
			#verific care e cel mai apropiat cluster de punctul noise_point
			closest_centroid = 0
			minDist = 99999
			for centroid in intermediary_centroids:
				for pixel in cluster_points[centroid]:
					dist = self.DistFunc(noise_point, pixel)
					if(dist < minDist):
						minDist = dist
						closest_centroid = centroid
			cluster_points[closest_centroid].append(noise_point)

		self.evaluate_cluster(clase_points, cluster_points)
		print("Evaluation")
		print("==============================")
		
		if(self.no_dims==2):
			plt.contourf(xx, yy, f, cmap='Blues')
			#afisare finala
			for k in cluster_points:
				c = self.random_color_scaled()
				for point in cluster_points[k]:
					plt.scatter(point[0], point[1], color=c)

			plt.show()


'''
=============================================
ALGORITM MARIACLUST
'''
if __name__ == "__main__":
	filename = sys.argv[1]
	no_clusters = int(sys.argv[2]) #no clusters
	no_bins = int(sys.argv[3]) #no bins
	expand_factor = float(sys.argv[4]) # expantion factor how much a cluster can expand based on the number of neighbours -- factorul cu care inmultesc closest mean (cat de mult se poate extinde un cluster pe baza vecinilor)
	cluster_distance = int(sys.argv[5])
	no_dims = int(sys.argv[6]) #no dims
	'''
	how you compute the dinstance between clusters:
	1 = centroid linkage
	2 = average linkage
	3 = single linkage
	4 = average linkage ponderat
	'''

	#read from file

	each_dimension_values = collections.defaultdict(list)
	dataset_xy = list()
	dataset_xy_validate = list()
	clase_points = collections.defaultdict(list)

	with open(filename) as f:
			content = f.readlines()

	content = [l.strip() for l in content]

	for l in content:
		aux = l.split('\t')
		for dim in range(no_dims):
			each_dimension_values[dim].append(float(aux[dim]))
		list_of_coords = list()
		for dim in range(no_dims):
			list_of_coords.append(float(aux[dim]))
		dataset_xy.append(list_of_coords)
		dataset_xy_validate.append(int(aux[no_dims]))
		clase_points[int(aux[no_dims])].append(tuple(list_of_coords))

	mariaClustInstance = MariaClust(no_clusters, no_bins, expand_factor, cluster_distance, no_dims)
	mariaClustInstance.cluster_dataset(dataset_xy, dataset_xy_validate, each_dimension_values, clase_points)


