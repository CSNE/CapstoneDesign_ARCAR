# Helper functions for treating tuples as vectors
import math

class TupleArithmeticError(ValueError):
	pass
	
class Tuples:
	@classmethod
	def dimension_equal(cls,d,*vs):
		for v in vs:
			if len(v) != d:
				return False
		return True
	@classmethod
	def nonempty_assert(cls,l):
		if len(l)==0:
			raise TupleArithmeticError("Need an operand!")
	@classmethod
	def dimension_match_assert(cls,*vs):
		cls.nonempty_assert(vs)
		if not cls.dimension_equal(len(vs[0]),*vs):
			raise TupleArithmeticError("Tuple size mismatch!")
	@classmethod
	def dimension_equal_assert(cls,d,*vs):
		cls.nonempty_assert(vs)
		if not cls.dimension_equal(d,*vs):
			raise TupleArithmeticError(F"Tuple size must be {d}!")
	@classmethod
	def elementwise_func(cls,f,*vs):
		cls.dimension_match_assert(*vs)
		# iV vector index / iE element index
		res=[]
		for iE in range(len(vs[0])):
			#print([vs[iV][iE] for iV in range(len(vs))])
			#print(*[vs[iV][iE] for iV in range(len(vs))])
			#print(f(*[vs[iV][iE] for iV in range(len(vs))]))
			res.append(f(*[vs[iV][iE] for iV in range(len(vs))]))
		return tuple(res)
	@classmethod
	def add(cls,*vs):
		return cls.elementwise_func(lambda *xs:sum(xs),*vs)
	@classmethod
	def neg(cls,v):
		return cls.elementwise_func(lambda x:-x,v)
	@classmethod
	def sub(cls,v,u):
		return cls.add(v,cls.neg(u))
	@classmethod
	def mult(cls,v,n):
		return cls.elementwise_func(lambda x:x*n,v)
	@classmethod
	def div(cls,v,n):
		return cls.mult(v,1/n)
	@classmethod
	def elementwise_mult(cls,u,v):
		return cls.elementwise_func(lambda a,b:a*b,u,v)
	@classmethod
	def dot(cls,v,u):
		return sum(cls.elementwise_mult(v,u))
	@classmethod
	def mag(cls,v):
		return math.sqrt(cls.dot(v,v))
	@classmethod
	def normalize(cls,v):
		return cls.div(v,cls.mag(v))
	@classmethod
	def cosine_between(cls,v,u):
		return cls.dot(cls.normalize(v),cls.normalize(u))
	@classmethod
	def degree_between(cls,v,u):
		return math.degrees(math.acos(cls.cosine_between(v,u)))
	@classmethod
	def rotate(cls,v,deg=None,rad=None):
		cls.dimension_equal_assert(2,v)
		if rad is None:
			rad=math.radians(deg)
		return (v[0]*math.cos(rad)-v[1]*math.sin(rad),
		        v[0]*math.sin(rad)+v[1]*math.cos(rad))
	@classmethod
	def degree(cls,v):
		cls.dimension_equal_assert(2,v)
		return math.degrees(math.atan2(v[1],v[0]))
	

if __name__=="__main__":
	print("DE",Tuples.dimension_equal((1,2),(3,4)))
	print("DE",Tuples.dimension_equal((1,2),(3,4,5)))
	print("AD",Tuples.add((1,2),(3,4)))
	print("NG",Tuples.neg((1,2)))
	print("SB",Tuples.sub((1,2),(3,4)))
	print("ML",Tuples.mult((1,2),2))
	print("DV",Tuples.div((1,2),2))
	print("EM",Tuples.elementwise_mult((1,2),(3,4)))
	print("DT",Tuples.dot((1,2),(3,4)))
	print("MG",Tuples.mag((1,2)))
	print("NM",Tuples.normalize((1,2)))
	print("RO",Tuples.rotate((1,2),deg=90))
