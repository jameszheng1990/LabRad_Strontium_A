import numpy as np
import h5py, json

def get_pixel_size_absorption():
    return 4.40 # [um]

def get_pulse():
    return 2 # us

def get_qe():
    qe = 0.793
    loss = 9.5/11.5
    viewport = 0.95
    bp_filter = 0.55
    calibration_path = "C:\LabRad\SrData\camera_calibration\ixon_absorption_imaging_calibration\\fitted_result.txt"
    with open(calibration_path, 'r') as file:
       f1 = file.read()
       f2 = json.loads(f1)
    q_factor = f2['q_factor']
    return qe*loss*bp_filter/viewport* q_factor

def get_ccd_gain(em_gain):
    em_gain_range = (0, 300)
    calibration_path = "C:\\LabRad\\SrData\\camera_calibration\\ixon_gain_measurement\\fitted_result.txt"
    with open(calibration_path, 'r') as file:
       f1 = file.read()
       f2 = json.loads(f1)
    a = f2['a']
    b = f2['b']
    if em_gain is not None:
        em_gain = sorted([em_gain_range[0], em_gain, em_gain_range[1]])[1]
    else:
        em_gain = 1
    return a*em_gain + b

def process_image(image_path, record_type, record_settings):
    images = {}
    images_h5 = h5py.File(image_path, "r")
    for key in images_h5:
        images[key] = np.array(images_h5[key], dtype='float64')
    images_h5.close()
    
    em_gain = record_settings.get('em_gain')
    
    if record_type == 'g_abs_img':  #
        return process_images_g(images, em_gain)
    elif record_type == 'eg':
        return process_images_eg(images)
    elif record_type == 'fast-g':
        return process_images_fast_g(images)
    elif record_type == 'fast-eg':
        return process_images_fast_eg(images)
    elif record_type == 'g_fluo_img':
        return process_images_g_fluorescence(images)
    elif record_type == 'raw':
        return process_images_raw(images)
    elif record_type == 'gain_calibration':
        return process_images_gain_calibration(images)

def process_images_g(images = None, em_gain = None):
    """ process images of g atoms """
    pixel_size = get_pixel_size_absorption() # [um]
    cross_section = 0.1014 # [um^2]
    linewidth = 201.06192983 # [ns?]
    pulse_length = get_pulse() # [us]
    efficiency = get_qe()
    gain = get_ccd_gain(em_gain)
    
    low_intensity_coefficient = pixel_size**2 / cross_section
    high_intensity_coefficient = 2 / (linewidth * pulse_length * efficiency * gain)
    
    bright = np.array(images['bright'], dtype='f')
    image = np.array(images['image'], dtype='f')
    dark = np.array(images['dark'], dtype='f')
    mean_dark = np.mean(dark)
#    image, bright = fix_image_gradient(image, bright, settings['norm'])
    
    n = (
        low_intensity_coefficient * np.log(abs(bright-mean_dark)/abs(image-mean_dark))
        # low_intensity_coefficient * np.log(bright)/(image)
        + high_intensity_coefficient * (bright - image)
        )
    
    return np.fliplr(n)

def process_images_eg(images):
    """ process images of e and g atoms """
    pixel_size = get_pixel_size_absorption() # [um]
    cross_section = 0.1014 # [um^2]
    linewidth = 201.06192983 # [ns?]
    pulse_length = 10 # [us]
    efficiency = 0.50348 
    gain = 0.25
    
    high_intensity_coefficient = 2 / (linewidth * pulse_length * efficiency * gain)
    low_intensity_coefficient = pixel_size**2 / cross_section
    
    bright = np.array(images['bright'], dtype='f') #- np.array(images['dark_bright'], dtype='f')
    image_g = np.array(images['image_g'], dtype='f') #- np.array(images['dark_g'], dtype='f')
    image_e = np.array(images['image_e'], dtype='f') #- np.array(images['dark_e'], dtype='f')
    
    n_g = (
        low_intensity_coefficient * np.log(bright / image_g)
        + high_intensity_coefficient * (bright - image_g)
        )[10:-10,:]
    
    n_e = (
        low_intensity_coefficient * np.log(bright / image_e)
        + high_intensity_coefficient * (bright - image_e)
        )[10:-10,:]

    n_g[:10,:] = 0
    n_g[-10:,:] = 0
    n_e[:10,:] = 0
    n_e[-10:,:] = 0
    
    return np.flipud(np.fliplr(np.vstack((n_e, n_g))))
#    return np.flipud(np.fliplr(np.vstack((image_e, image_g))))

def process_images_fast_g(images):
    """ process fast images of g atoms """
    pixel_size = 7.3 # [um]
    cross_section = 0.1014 # [um^2]
    linewidth = 201.06192983 # [ns?]
    pulse_length = 3 # [us]
    efficiency = 0.50348 
    gain = 0.25
    
    high_intensity_coefficient = 2 / (linewidth * pulse_length * efficiency * gain)
    low_intensity_coefficient = pixel_size**2 / cross_section
    
    bright = np.array(images['bright'], dtype='f')
    image = np.array(images['image'], dtype='f')
    
    n = (
        low_intensity_coefficient * np.log(bright / image)
        + high_intensity_coefficient * (bright - image)
        )
    
    return np.flipud(np.fliplr(n))

def process_images_fast_eg(images):
    """ process fast images of e and g atoms """
    pixel_size = 7.3 # [um]
    cross_section = 0.1014 # [um^2]
    linewidth = 201.06192983 # [ns?]
    pulse_length = 3 # [us]
    efficiency = 0.50348 
    gain = 0.25
    
    high_intensity_coefficient = 2 / (linewidth * pulse_length * efficiency * gain)
    low_intensity_coefficient = pixel_size**2 / cross_section

    bright = np.array(images['bright'], dtype='f') #- np.array(images['dark_bright'], dtype='f')
    image_g = np.array(images['image-g'], dtype='f') #- np.array(images['dark_g'], dtype='f')
    image_e = np.array(images['image-e'], dtype='f') #- np.array(images['dark_e'], dtype='f')
    
    n_g = (
        low_intensity_coefficient * np.log(bright / image_g)
        + high_intensity_coefficient * (bright - image_g)
        )
    
    n_e = (
        low_intensity_coefficient * np.log(bright / image_e)
        + high_intensity_coefficient * (bright - image_e)
        )
    
    photon_counts = bright / (gain * efficiency)
    photon_flux = photon_counts / (pixel_size**2 * pulse_length)
    saturation_flux = linewidth / (2 * cross_section)
    
    n_p = photon_flux / saturation_flux / 2

    return np.flipud(np.fliplr(np.vstack((n_g, n_e, n_p))))

def process_images_g_fluorescence(images = None, em_gain = None):
    image = np.array(images['image'], dtype = 'f')
    bright = np.array(images['bright'], dtype = 'f')
    n = image - bright
    # n = image
    # n *= fluorescence()
    
    return np.fliplr(n)

def process_images_raw(images):
    bright = np.array(images['bright'], dtype = 'f')
    dark = np.array(images['dark'], dtype = 'f')
    return bright

def process_images_gain_calibration(images):
    a = np.array(images['a'], dtype = 'f')
    b = np.array(images['b'], dtype = 'f')
    dark = np.array(images['dark'], dtype = 'f')
    n = a - dark
    return np.fliplr(n)

def process_images_absorption_calibration(images, em_gain):
    pixel_size = get_pixel_size_absorption() # [um]
    cross_section = 0.1014 # [um^2]
    linewidth = 201.06192983 # [ns?]
    pulse_length = get_pulse() # [us]
    efficiency = get_qe()
    gain = get_ccd_gain(em_gain)
    
    low_intensity_coefficient = pixel_size**2 / cross_section
    high_intensity_coefficient = 2 / (linewidth * pulse_length * efficiency * gain)
    
    bright = np.array(images['bright'], dtype='f')
    image = np.array(images['image'], dtype='f')
    dark = np.array(images['dark'], dtype='f')
    mean_dark = np.mean(dark)
#    image, bright = fix_image_gradient(image, bright, settings['norm'])
    
    n_low = low_intensity_coefficient * np.log(abs(bright-mean_dark)/abs(image-mean_dark))
    n_high =high_intensity_coefficient * (bright - image)        
    
    return np.fliplr(n_high), np.fliplr(n_low)