import collections
import geolocation

BuildingDef = collections.namedtuple(
	"BuildingDef",
	["latitude","longitude","name"])

buildings=[
	BuildingDef(
		latitude=37.56079890673998,
		longitude=126.93547900020101,
		name="공학원"),
	BuildingDef(
		latitude=37.561792015053406,
		longitude=126.93509213418382,
		name="제3공학관")
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

