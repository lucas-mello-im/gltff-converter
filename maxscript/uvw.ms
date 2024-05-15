fn copy_uvw_from_to obj from_uvw_channel to_uvw_channel =
(
	try
	(
		polyop.setNumMapVerts obj to_uvw_channel (polyop.getNumMapVerts obj from_uvw_channel ) keep:false
		polyop.setNumMapFaces obj to_uvw_channel (polyop.getNumMapFaces obj from_uvw_channel)  keep:false

		for v = 1 to (polyop.getNumMapVerts obj to_uvw_channel) do 
		(
			polyop.setMapVert obj to_uvw_channel v (polyop.getMapVert obj from_uvw_channel v)
		)

		for f = 1 to (polyop.getNumMapFaces obj to_uvw_channel) do
		(
			polyop.setMapFace obj to_uvw_channel f (polyop.getMapFace obj from_uvw_channel f)
		)
		print ("UVW channel " +(from_uvw_channel as string) + " copied to channel " +(to_uvw_channel as string) + " for " + (obj.name as string))
	)
	catch 
	(
		print "--- error while copying UVW channels"
		return false
	)
)
convertToPoly $
copy_uvw_from_to $ 2 1