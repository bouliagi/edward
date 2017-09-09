from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import edward as ed
import numpy as np
import tensorflow as tf

from edward.models import Bernoulli, Categorical, Multinomial, Normal


class test_evaluate_class(tf.test.TestCase):

  def test_metrics(self):
    with self.test_session():
      x = Normal(loc=0.0, scale=1.0)
      x_data = tf.constant(0.0)
      ed.evaluate('mean_squared_error', {x: x_data}, n_samples=1)
      ed.evaluate(['mean_squared_error'], {x: x_data}, n_samples=1)
      ed.evaluate(['mean_squared_error', 'mean_absolute_error'],
                  {x: x_data}, n_samples=1)
      self.assertRaises(TypeError, ed.evaluate, x, {x: x_data}, n_samples=1)
      self.assertRaises(NotImplementedError, ed.evaluate, 'hello world',
                        {x: x_data}, n_samples=1)

  def test_metrics_classification(self):
    with self.test_session():
      x = Bernoulli(probs=0.51)
      x_data = tf.constant(1)
      self.assertAllClose(
          1.0,
          ed.evaluate('binary_accuracy', {x: x_data}, n_samples=1))
      x = Bernoulli(probs=0.51, sample_shape=5)
      x_data = tf.constant([1, 1, 1, 0, 0])
      self.assertAllClose(
          0.6,
          ed.evaluate('binary_accuracy', {x: x_data}, n_samples=1))
      x = Bernoulli(probs=tf.constant([0.51, 0.49, 0.49]))
      x_data = tf.constant([1, 0, 1])
      self.assertAllClose(
          2.0 / 3,
          ed.evaluate('binary_accuracy', {x: x_data}, n_samples=1))

      x = Categorical(probs=tf.constant([0.48, 0.51, 0.01]))
      x_data = tf.constant(1)
      self.assertAllClose(
          1.0,
          ed.evaluate('sparse_categorical_accuracy', {x: x_data}, n_samples=1))
      x = Categorical(probs=tf.constant([0.48, 0.51, 0.01]), sample_shape=5)
      x_data = tf.constant([1, 1, 1, 0, 2])
      self.assertAllClose(
          0.6,
          ed.evaluate('sparse_categorical_accuracy', {x: x_data}, n_samples=1))
      x = Categorical(
          probs=tf.constant([[0.48, 0.51, 0.01], [0.51, 0.48, 0.01]]))
      x_data = tf.constant([1, 2])
      self.assertAllClose(
          0.5,
          ed.evaluate('sparse_categorical_accuracy', {x: x_data}, n_samples=1))

      x = Multinomial(total_count=1.0, probs=tf.constant([0.48, 0.51, 0.01]))
      x_data = tf.constant([0, 1, 0], dtype=x.dtype.as_numpy_dtype)
      self.assertAllClose(
          1.0,
          ed.evaluate('categorical_accuracy', {x: x_data}, n_samples=1))
      x = Multinomial(total_count=1.0, probs=tf.constant([0.48, 0.51, 0.01]),
                      sample_shape=5)
      x_data = tf.constant(
          [[0, 1, 0], [0, 1, 0], [0, 1, 0], [1, 0, 0], [0, 0, 1]],
          dtype=x.dtype.as_numpy_dtype)
      self.assertAllClose(
          0.6,
          ed.evaluate('categorical_accuracy', {x: x_data}, n_samples=1))

  def test_data(self):
    with self.test_session():
      x_ph = tf.placeholder(tf.float32, [])
      x = Normal(loc=x_ph, scale=1.0)
      y = 2.0 * Normal(loc=0.0, scale=1.0)
      x_data = tf.constant(0.0)
      x_ph_data = np.array(0.0)
      y_data = tf.constant(20.0)
      ed.evaluate('mean_squared_error', {x: x_data, x_ph: x_ph_data},
                  n_samples=1)
      ed.evaluate('mean_squared_error', {y: y_data}, n_samples=1)
      self.assertRaises(TypeError, ed.evaluate, 'mean_squared_error',
                        {'y': y_data}, n_samples=1)

  def test_n_samples(self):
    with self.test_session():
      x = Normal(loc=0.0, scale=1.0)
      x_data = tf.constant(0.0)
      ed.evaluate('mean_squared_error', {x: x_data}, n_samples=1)
      ed.evaluate('mean_squared_error', {x: x_data}, n_samples=5)
      self.assertRaises(TypeError, ed.evaluate, 'mean_squared_error',
                        {x: x_data}, n_samples='1')

  def test_output_key(self):
    with self.test_session():
      x_ph = tf.placeholder(tf.float32, [])
      x = Normal(loc=x_ph, scale=1.0)
      y = 2.0 * x
      x_data = tf.constant(0.0)
      x_ph_data = np.array(0.0)
      y_data = tf.constant(20.0)
      ed.evaluate('mean_squared_error', {x: x_data, x_ph: x_ph_data},
                  n_samples=1)
      ed.evaluate('mean_squared_error', {y: y_data, x_ph: x_ph_data},
                  n_samples=1)
      ed.evaluate('mean_squared_error', {x: x_data, y: y_data, x_ph: x_ph_data},
                  n_samples=1, output_key=x)
      self.assertRaises(KeyError, ed.evaluate, 'mean_squared_error',
                        {x: x_data, y: y_data, x_ph: x_ph_data}, n_samples=1)
      self.assertRaises(TypeError, ed.evaluate, 'mean_squared_error',
                        {x: x_data, y: y_data, x_ph: x_ph_data}, n_samples=1,
                        output_key='x')

if __name__ == '__main__':
  tf.test.main()
