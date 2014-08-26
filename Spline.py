
#original author - Ian Mallett
#graciously allowed the use of this code ( - Kochanek-Bartels Spline - 1.0.0 - May 2008) under the GPL

class Spline():

	def __init__(self, stepsize = 1./4., c=0, b=0, t=0):
		self.c = c
		self.b = b
		self.t = t
		self.ControlPoints = []
		self.subpoints = []
		self.stepsize = stepsize
		self.selected_point = None
	def add_or_select(self, mpos, selection_dist):
		nearest, dist2, nindex = self.nearestPoint((mpos[0],mpos[1]))
		#print "\n"
		if dist2 < selection_dist**2:
			selected = nindex
		else:
			selected = self.add_point((mpos[0],mpos[1]))
		self.selected_point = selected
		#print selected
		return selected
	def remove_point(self, mpos, selection_dist):
		nearest, dist2, nindex = self.nearestPoint((mpos[0],mpos[1]))
		#print "\n"
		if dist2 < selection_dist**2:
			self.ControlPoints.remove(nearest)
	def add_point(self, mpos):
		if len(self.ControlPoints) < 3:
			self.ControlPoints.append(mpos)
			return len(self.ControlPoints)-1
		snearest, sdist2, snindex = self.nearestSubPoint(mpos)
		nsindex = snindex*self.stepsize
		nindex = int(nsindex+0.5)
		#print nsindex, nindex
		test =  nsindex- nindex
		#print test
		if test>0 and test < 2:
			nindex+=1
		self.ControlPoints.insert(nindex, (mpos[0],mpos[1]))
		return nindex
		
	def nearestPoint(self, pos):
		return self._nearest(pos, self.ControlPoints)
	
	def nearestSubPoint(self, pos):
		return self._nearest(pos, self.subpoints)
	def _nearest(self, pos, points):
		shortest = 999999
		nearest = None
		index = -1
		retindex = 0
		for p in points:
			index+=1
			xd = p[0]-pos[0]
			yd = p[1]-pos[1]
			td = xd*xd+yd*yd
			if td<shortest:
				shortest = td
				nearest = p
				retindex = index
		return nearest, shortest, retindex
			

	def DrawCurve(self):

		c=self.c
		b=self.b
		t=self.t
		ControlPoints = self.ControlPoints
		
		#make into a closed loo[
		ControlPoints=[ControlPoints[-1]]+ControlPoints+ControlPoints[0:2]
		#print ControlPoints
		tans = []

		tand = []

		for x in xrange(len(ControlPoints)-2):

			tans.append([])

			tand.append([])



		cona = (1-t)*(1+b)*(1-c)*0.5

		conb = (1-t)*(1-b)*(1+c)*0.5

		conc = (1-t)*(1+b)*(1+c)*0.5

		cond = (1-t)*(1-b)*(1-c)*0.5



		i = 1

		while i < len(ControlPoints)-1:

			pa = ControlPoints[i-1]

			pb = ControlPoints[i]

			pc = ControlPoints[i+1]

					

			x1 = pb[0] - pa[0]

			y1 = pb[1] - pa[1]

			#z1 = pb[2] - pa[2]

			x2 = pc[0] - pb[0]

			y2 = pc[1] - pb[1]

			#z2 = pc[2] - pb[2]

					

			tans[i-1] = (cona*x1+conb*x2, cona*y1+conb*y2) #cona*z1+conb*z2

			tand[i-1] = (conc*x1+cond*x2, conc*y1+cond*y2) #conc*z1+cond*z2

			

			i += 1



		#render spline (Your camera part)

		t_inc = self.stepsize#0.2

		i = 1
		
		finalLines = []

		while i < len(ControlPoints)-2:

			p0 = ControlPoints[i]

			p1 = ControlPoints[i+1]

			m0 = tand[i-1]

			m1 = tans[i]

			#draw curve from p0 to p1

			Lines = [(p0[0],p0[1])]

			t_iter = t_inc

			while t_iter < 1.0:

				h00 = ( 2*(t_iter**3)) - ( 3*(t_iter**2)) + 1

				h10 = ( 1*(t_iter**3)) - ( 2*(t_iter**2)) + t_iter

				h01 = (-2*(t_iter**3)) + ( 3*(t_iter**2))

				h11 = ( 1*(t_iter**3)) - ( 1*(t_iter**2))

				px = h00*p0[0] + h10*m0[0] + h01*p1[0] + h11*m1[0]

				py = h00*p0[1] + h10*m0[1] + h01*p1[1] + h11*m1[1]

				#pz = h00*p0[2] + h10*m0[2] + h01*p1[2] + h11*m1[2]

				Lines.append((px,py))

				t_iter += t_inc

			Lines.append((p1[0],p1[1]))

			Lines2 = []

			for p in Lines:

				Lines2.append((int(round(p[0])),int(round(p[1]))))

			#pygame.draw.aalines(Surface,(255,255,255),False,Lines2)
			finalLines.extend(Lines2[:-1])

			i += 1
		finalLines.append(Lines2[-1])
		self.subpoints = finalLines
		return finalLines
