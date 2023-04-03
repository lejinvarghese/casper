import tensorflow as tf

print(tf.sysconfig.get_build_info())

print(tf.config.list_physical_devices("GPU"))