import collections
import geolocation

BuildingDef = collections.namedtuple(
	"BuildingDef",
	["latitude","longitude","name"])

buildings=[
	BuildingDef(
		latitude=37.56082028116716, 
		longitude=126.9353526867473,
		name="공학원"),
	BuildingDef(
		latitude=37.561477325183965, 
		longitude=126.93596955291314,
		name="1공학관(S)"),
	BuildingDef(
		latitude=37.56218007992962, 
		longitude=126.93624260527221,
		name="1공학관(N)"),
	BuildingDef(
		latitude=37.56173031643782, 
		longitude=126.93657948873086,
		name="1공학관"),
	BuildingDef(
		latitude=37.561842757551894, 
		longitude=126.93603692851528,
		name="4공학관"),
	BuildingDef(
		latitude=37.56173031568103, 
		longitude=126.93513621286633,
		name="3공학관"),
	BuildingDef(
		latitude=37.562300949412595, 
		longitude=126.93520003956498,
		name="2공학관"),
	BuildingDef(
		latitude=37.56269729859164, 
		longitude=126.9355440191072,
		name="스포츠과학관"),
	BuildingDef(
		latitude=37.563088026169765, 
		longitude=126.93572487599894,
		name="체육관"),
	BuildingDef(
		latitude=37.56294185162516, 
		longitude=126.93444471576267,
		name="IBS관"),
	BuildingDef(
		latitude=37.563338198103764, 
		longitude=126.93466457739468,
		name="과학원"),
	BuildingDef(
		latitude=37.56408131456686, 
		longitude=126.93474450888216,
		name="과학관"),
	BuildingDef(
		latitude=37.56312983169124, 
		longitude=126.93380726576062,
		name="첨단과학기술연구관")
	]
	

	
BuildingLGC= collections.namedtuple(
	"BuildingLGC",
	["lgc","name"])
buildings_lgc=[]
for b in buildings:
	buildings_lgc.append(
		BuildingLGC(
			lgc=geolocation.LocalGroundCoordinates.from_lla(
				latitude=b.latitude,
				longitude=b.longitude,
				altitude=0),
			name=b.name))

