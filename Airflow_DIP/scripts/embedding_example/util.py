import io
import tensorflow as tf


def get_embedding_columns(informative_terms_path, dimension):
    with io.open(informative_terms_path, 'r', encoding='utf8') as f:
        # Convert it to a set first to remove duplicates.
        informative_terms = sorted(list(set(f.read().split())))

    terms_feature_column = tf.feature_column.categorical_column_with_vocabulary_list(
        key="terms",
        vocabulary_list=informative_terms)
    terms_embedding_column = tf.feature_column.embedding_column(
        terms_feature_column, dimension=dimension)
    return terms_embedding_column

def _parse_function(record):
    """Extracts features and labels.

    Args:
      record: File path to a TFRecord file
    Returns:
      A `tuple` `(labels, features)`:
        features: A dict of tensors representing the features
        labels: A tensor with the corresponding labels.
    """
    features = {
        "terms": tf.VarLenFeature(dtype=tf.string),
    # terms are strings of varying lengths
        "labels": tf.FixedLenFeature(shape=[1], dtype=tf.float32)
    # labels are 0 or 1
    }

    parsed_features = tf.parse_single_example(record, features)

    terms = parsed_features['terms'].values
    labels = parsed_features['labels']

    return {'terms': terms}, labels


def _input_fn(input_filenames, num_epochs=None, shuffle=True):
    # Same code as above; create a dataset and map features and labels.
    ds = tf.data.TFRecordDataset(input_filenames)
    ds = ds.map(_parse_function)

    if shuffle:
        ds = ds.shuffle(10000)

    # Our feature data is variable-length, so we pad and batch
    # each field of the dataset structure to whatever size is necessary.
    ds = ds.padded_batch(25, ds.output_shapes)

    ds = ds.repeat(num_epochs)

    # Return the next batch of data.
    features, labels = ds.make_one_shot_iterator().get_next()
    return features, labels