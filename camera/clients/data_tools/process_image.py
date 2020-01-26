import numpy as np
import h5py


def process_image(image_path, record_type):
    images = {}
    images_h5 = h5py.File(image_path, "r")
    for key in images_h5:
        images[key] = np.array(images_h5[key], dtype='float64')
    images_h5.close()
    if record_type == 'g': 
        return process_images_g(images)
    elif record_type == 'eg':
        return process_images_eg(images)
    elif record_type == 'fast-g':
        return process_images_fast_g(images)
    elif record_type == 'fast-eg':
        return process_images_fast_eg(images)
    elif record_type == 'abs_img':
        return process_images_absorption_images(images)
    elif record_type == 'fluo_img':
        return process_images_fluorescence_images(images)

def process_images_g(images):
    """ process images of g atoms """
    pixel_size = 0.55793991 # [um]
    cross_section = 0.1014 # [um^2]
    linewidth = 201.06192983 # [ns?]
    pulse_length = 3 # [us]
    efficiency = 0.50348 
    gain = 0.25
    high_intensity_coefficient = 2 / (linewidth * pulse_length * efficiency * gain)
    low_intensity_coefficient = pixel_size**2 / cross_section
    
    bright = np.array(images['bright'], dtype='f')
    image = np.array(images['image'], dtype='f')
    
#    image, bright = fix_image_gradient(image, bright, settings['norm'])
    
    n = (
        low_intensity_coefficient * np.log(bright / image)
        + high_intensity_coefficient * (bright - image)
        )
    return np.flipud(np.fliplr(n))

def process_images_eg(images):
    """ process images of e and g atoms """
    pixel_size = 0.55793991 # [um]
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
    pixel_size = 0.55793991 # [um]
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
    pixel_size = 0.55793991 # [um]
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

def process_images_absorption_images(images):
    """ process absoprtion images, return calibrated OD images."""
    pixel_size = 0.55793991 # [um]
    cross_section = 0.1014 # [um^2]
    linewidth = 201.06192983 # [ns?]
    pulse_length = 3 # [us]
    efficiency = 0.50348 
    gain = 0.25
    
    image = np.array(images['image'], dtype='f')
    bright = np.array(images['bright'], dtype='f')
    dark = np.array(images['dark'], dtype='f')
    
    od = (
        np.log(abs(bright - dark + 0.001)/abs(image - dark+ 0.001))
          )
    
    return np.flipud(np.fliplr(od))

def process_images_fluorescence_images(images):
    image = np.array(images['image'], dtype = 'f')
    bright = np.array(images['bright'], dtype = 'f')
    
    atoms = image - bright
    
    return np.flipud(np.fliplr(atoms))