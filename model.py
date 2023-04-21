# import tensorflow as tf
# print(tf.sysconfig.get_build_info())
# print(tf.config.list_physical_devices("GPU"))


def get_response(query, model, tokenizer):
    input_ids = tokenizer.encode(query, return_tensors="tf")

    output = model.generate(
        input_ids,
        min_length=5,
        max_length=100,
        top_k=40,
        top_p=0.9,
    )
    return tokenizer.decode(output[0], skip_special_tokens=True)
