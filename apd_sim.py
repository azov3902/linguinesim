############################################################################################
#
# 	File:		apd_sim.py
#	Author:		Anna Zovaro
#	Email:		anna.zovaro@anu.edu.au
#	Edited:		29/05/2016
#
#	Description:
#	Simulate images of galaxies imaged using the APD detector within the ANU 2.3 m telescope.
#
#	TO DO:
#	- implement cross-correlation
#	- write shift-and-stack routine
#	- write routine to generate images 
#	- multi-thread processing
#	- simulate tip and tilt distortion.
#	- implement poisson noise (not Gaussian)
#
############################################################################################

import apdParameters as detector
import anu23mParameters as telescope
import cryoParameters as cryo
from apd_etc import *
import pdb

import numpy as np
import numpy.fft
from astropy.io import fits
import matplotlib.pyplot as plt
import scipy.signal
import scipy.misc
import matplotlib
matplotlib.rc('image', interpolation='none', cmap = 'gray')
plt.close('all')

# """ Variables """
# # Imaging variables
# band = 'K'
# t_exp = 0.1						# exposure time
# N = 10							# number of images

# """ Imaging simulation """
# # Add signal.
# # hdulist = fits.open('sample-images/tadpole.fits')





# ##################################################################################
# """ Simulated high-res images """
# pad_width = 0
# img_size = N
# shift_y = 0
# shift_x = 0
# img_1 = np.copy(imgs[0])
# #TODO get the angular extent of the image from the FITS file? For now use a guessed value
# # theta_as = 10	# angular extent of image (arcsec)
# # plate_scale = theta_as / N 	# plate scale (arcsec/pixel)
# # Note: in the future the image size will be replaced with the detector size.

# # NOTE: using imresize does weird-ass things to the image
# # Use GIMP instead for resizing or find a way to do it in python
# # TODO: try to save in float32, not uint8
# img_1 = np.copy(scipy.misc.imresize(imgs[0], (img_size, img_size)))
# img_1 = np.pad(img_1, pad_width, mode='constant', constant_values=(0,0))
# img_2 = np.copy(img_1)
# img_2 = np.roll(img_2, shift_y, axis=0)
# img_2 = np.roll(img_2, shift_x, axis=1)

# conv_shift = scipy.signal.convolve2d(img_1, img_2)

# ##################################################################################
# """ Convolving a Gaussian kernel with a high-res image to simulate seeing """
# x = np.linspace(-10,+10,1)
# y = np.linspace(-10,+10,1)
# X, Y = np.meshgrid(x, y)
# w_0 = 4
# I_0 = 10
# # Gaussian kernel to simulate seeing in long exposure times
# kernel = I_0 * np.exp(- (np.power(X, 2) + np.power(Y, 2)) / (2 * w_0 * w_0))

# # conv_seeing = scipy.signal.convolve2d(img_1, kernel)

# ##################################################################################
# """ Convolving the PSF of the ANU 2.3 m telescope with a truth image to simulate diffraction-limited imaging """
# # Ideal diffraction-limited PSF of a telescope
# # TODO: to simulate diffraction-limited images with the 2.3 m telescope, need to know
# #	1. the diffraction limit of the telescope (compute lambda/D & convert to a PSF - estimate in different bands!)
# #	2. the angular size of the object we're simulating looking at - e.g. get a high-res image of some galaxy imaged by HST & 
# #		convolve it with the PSF of the 2.3 m (assume perfect circular aperture for now) to get a fake diffraction-limited
# #		image of the source. We need to make the plate scales of the truth image and PSF match for this to work

# # Calculating the diffraction limit
# band = 'J'
# wavelength = telescope.filter_bands_m[band][0]
# k = 2 * np.pi / wavelength

# # Calculating the PSF
# # in pixels
# x = np.arange(-detector.width/2, +detector.width/2, 1)
# y = np.arange(-detector.height/2, +detector.height/2, 1)
# X, Y = np.meshgrid(x, y)
# R = 2 * k / telescope.f_ratio * detector.l_px * np.sqrt(np.power(X,2) + np.power(Y,2))
# # Calculating the PSF
# I_0 = 1
# psf = I_0 * np.power(2 * scipy.special.jv(1, R) / R, 2)

# plt.figure()
# plt.imshow(psf)
# plt.title('PSF of ANU 2.3 m telescope')
# plt.xlabel('x (pixels)')
# plt.ylabel('y (pixels)')

# # conv_telescope = scipy.singal.convolve2d(img_1, psf)

# ##################################################################################
# f_1 = np.fft.fft2(img_1)
# f_2 = np.fft.fft2(img_2)

# # Finding the maximum
# idx = np.unravel_index(np.argmax(conv_shift), (2*N-1,2*N-1))

# # Let x and y be our two images. 
# # If x is simply y shifted, then X(u,v) and Y(u,v) will be the same in frequency space, but will be shifted apart in phase space. 

# # plt.figure()
# # plt.subplot(1,2,1)
# # plt.imshow(img_1)
# # plt.title('Image 1')
# # plt.subplot(1,2,2)
# # plt.imshow(img_2)
# # plt.title('Image 2')

# # plt.figure()
# # plt.subplot(2,2,1)
# # plt.imshow(np.real(f_1))
# # plt.title(r'$\mathbb{Re}(\mathcal{F}(img_1))$')
# # plt.subplot(2,2,2)
# # plt.imshow(np.imag(f_1))
# # plt.title(r'$\mathbb{Im}(\mathcal{F}(img_1))$')
# # plt.subplot(2,2,3)
# # plt.imshow(np.real(f_2))
# # plt.title(r'$\mathbb{Re}(\mathcal{F}(img_2))$')
# # plt.subplot(2,2,4)
# # plt.imshow(np.imag(f_2))
# # plt.title(r'$\mathbb{Im}(\mathcal{F}(img_2))$')

# # plt.figure()
# # plt.imshow(conv_shift)
# # plt.title('Convolution of shifted images')
# # # plt.colorbar()
# # plt.show()

#########################################################################################################
def getImages(fname,
	returnRawImages=False, 
	addNoise=False, 
	seeing=False, 
	source_plate_scale_as=0.05,
	detector_size_px=(detector.width_px, detector.height_px),
	dest_plate_scale_as=206256/telescope.efl_mm * 1e3 * detector.l_px
	):
	# 1. Load image from a FITS file (or other source).
	# fname='sample-images/ngc300_wfc.fits'
	# fname = 'sample-images/ngc300_wfpc2_1.fits'
	# fname = 'sample-images/ngc300_wfpc2_2.fits'
	# fname = 'sample-images/tadpole.fits'
	hdulist = fits.open(fname)

	images_raw = hdulist[0].data

	if returnRawImages:
		return images_raw

	if len(images_raw.shape) > 2:
		N = images_raw[0].shape[0]
		source_height_px = images_raw.shape[1]
		source_width_px = images_raw.shape[2]
	else:
		N = 1
		source_height_px = images_raw.shape[0]
		source_width_px = images_raw.shape[1]

	# source_plate_scale_as = 0.1
	source_width_as = source_width_px * source_plate_scale_as
	source_height_as = source_height_px * source_plate_scale_as

	hdulist.close()

	# 2. Simulate seeing conditions and resize to replicate the pixel scale of the detector:
	#	a. Get the angular extent of the source image:
	#		size(pixels on our detector) = size(of source, in as) / plate scale
	# dest_plate_scale_as = 206256/telescope.efl_mm * 1e3 * detector.l_px
	# dest_plate_scale_as = 0.5
	detector_width_px = detector_size_px[0]
	detector_height_px = detector_size_px[1]
	dest_width_px = source_width_as / dest_plate_scale_as
	dest_height_px = source_height_as / dest_plate_scale_as

	#	b. Rescale image to the appropriate size for our detector
	images = np.copy(images_raw)
	images = scipy.misc.imresize(images, dest_width_px/source_width_px)
	images = np.swapaxes(images,0,2)
	images = images.astype(np.float32)

	#	c. Resize to detector.length * detector.width, maintaining the format. Padding if necessary
	if dest_width_px > detector.width_px:
		images = images[:, images.shape[1]-detector_width_px/2:images.shape[1]+detector_width_px/2+1, :]
		pad_width = 0
	else: 
		pad_width = np.ceil(detector_width_px - dest_width_px)

	if dest_height_px > detector_height_px:
		images = images[:, :, images.shape[2]-detector_height_px/2:images.shape[2]+detector_height_px/2+1]
		pad_height = 0
	else:
		pad_height = np.ceil(detector_height_px - dest_height_px)

	pad_width = pad_width.astype(np.int)
	pad_height = pad_height.astype(np.int)
	images = np.pad(images, ((0, 0), (pad_width, pad_width), (pad_height, pad_height)), mode='constant')

	#	d. Convolve the resized image(s) with the PSF of the detector, or replicate seeing.

	# 3. Add noise.
	if addNoise:
		images = addNoise(images)

	return images	

#########################################################################################################
def addTurbulence(image, N, sigma=10):
	" Add turbulence to an input `truth' image. Returns N copies of the input image with randomised turbulence added. "
	# Tip and tilt for now	

	# Shift by some random amount
	images = np.ndarray((N, image.shape[0], image.shape[1]))
	tt_idxs = np.ndarray((N, 2))
	for k in range(N):
		shift_width = np.ceil(np.random.randn() * sigma).astype(int)
		shift_height = np.ceil(np.random.randn() * sigma).astype(int)
		images[k] = np.roll(np.roll(image, shift_width, 0), shift_height, 1)
		tt_idxs[k] = [shift_width, shift_height]

	return (images, tt_idxs)

#########################################################################################################
	# The noise sigmas are expressed in units of electrons
	# Need to multiply by the ADU gain to get counts
	# For every pixel, get a random number drawn from a Gaussian distribution scaled up by sigma for each noise source
	# and ceiling round it 
"""
	ADDING NOISE:
		The Sigmga * t_exp that get output by the ETC are *what we should theoretically expect to measure 
		in every single pixel*. 
		However, because we are dealing with low numbers of photons here, we assume that the standard deviation goes as 
		the square root of the total numbers of pixels (Poisson statistics)
		Therefore the noise that we add should be a Gaussian *Centered* at Sigma * t_exp (the theoretical count rate)
		+/- sqrt(Sigma * t_exp) 
		The actual statistical properties of the nosie (i.e. the standard deviation) are actually determined by Poisson
		statistics!
"""
def addNoise(images,band='H',surfaceBrightness=19,magnitudeSystem='AB',t_exp=0.1):
	# Creating an array in which to store the noisy images.
	N = images.shape[0]
	noisyImages = np.copy(images)

	# Getting noise parameters from the ETC.
	etc_output = exposureTimeCalc(band,t_exp,surfaceBrightness,magnitudeSystem)

	# Adding noise to each image.
	for k in range(N):
		frame_sky = np.ones((length, width)) * etc_output['N_sky'] + np.random.randn(length, width) * etc_output['sigma_sky']
		frame_dark = np.ones((length, width)) * etc_output['N_dark'] + np.random.randn(length, width) * etc_output['sigma_dark']
		frame_cryo = np.ones((length, width)) * etc_output['N_cryo'] + np.random.randn(length, width) * etc_output['sigma_cryo']
		frame_RN = np.ones((length, width)) * etc_output['N_RN'] + np.random.randn(length, width) * etc_output['sigma_RN']
		noisyImages[k] += frame_sky + frame_cryo + frame_RN + frame_dark

	return noisyImages


#########################################################################################################
def shiftAndStack(images, plotIt=False):
	" Shift and stack N images given in the array of N images."
	if (len(images.shape) > 2):
		N = images.shape[0]-1	# subtract one because we use the first image as a reference
	else:
		return -1

	# For now, we use the first image in the array as the reference: i.e. we align all other images to this image.
	image_ref = np.copy(images[0])			# 'reference' image
	image_stacked = np.copy(images[0])		# shifted-and-stacked image
	images = np.copy(images[1:])	

	width = images[0].shape[0]
	height = images[0].shape[1]
	
	corrs = np.ndarray((N, 2 * width - 1, 2 * height - 1))	# Array to hold x-correlation results
	corr_peak_idxs = np.ndarray((N, 2))		# indices of the peak value in the x-correlation
	img_peak_idxs = np.ndarray((N, 2))		# shift in x and y computed from the x-correlation

	for k in range(N):
		# Cross-correlate image k with the reference image to find the tip and tilt.
		corrs[k] = scipy.signal.fftconvolve(image_ref, images[k][::-1,::-1])
		corr_peak_idxs[k] = np.unravel_index(np.argmax(corrs[k]), (2 * width - 1, 2 * height - 1))
		img_peak_idxs[k][0] = - corr_peak_idxs[k][0] + (width - 1)
		img_peak_idxs[k][1] = - corr_peak_idxs[k][1] + (height - 1)

		# Shift-and-stack the images.
		image_stacked += np.roll(np.roll(images[k], -img_peak_idxs[k][0].astype(int), 0), -img_peak_idxs[k][1].astype(int), 1)	

		# Plotting
		if plotIt:
			if k == 0:
				plt.figure()
				plt.subplot(1,3,1)
				plt.imshow(images[0],origin='lower')
				plt.subplot(1,3,2)
				scat2 = plt.scatter(0.0,0.0,c='r',s=20)
				plt.subplot(1,3,3)
				scat3 = plt.scatter(0.0,0.0,c='g',s=40)

			plt.subplot(1,3,2)
			plt.imshow(images[k],origin='lower')	
			plotcoords = np.ndarray((2))
			plotcoords[1] = img_peak_idxs[k,0] + width / 2
			plotcoords[0] = img_peak_idxs[k,1] + height / 2
			scat2.set_offsets(plotcoords)

			plt.subplot(1,3,3)
			plt.imshow(corrs[k],interpolation='nearest',origin='lower')
			corr_peak_coords = np.ndarray((2))
			corr_peak_coords[0] = corr_peak_idxs[k][1]
			corr_peak_coords[1] = corr_peak_idxs[k][0]
			scat3.set_offsets(corr_peak_coords)

			# plt.scatter([peak_idxs[k][0]], [peak_idxs[k][1]], c='r', s=20)
			plt.draw()
			plt.pause(1)

	return image_stacked