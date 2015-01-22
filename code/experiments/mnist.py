"""
Train a mixture of Bernoullis on MNIST data.
"""

import os
import sys

sys.path.append('./code')

from argparse import ArgumentParser
from matplotlib.pyplot import imsave
from tools import stitch, Experiment
from numpy import load, round, asarray, hstack
from numpy.random import rand, permutation
from trmix import MoBernoulli

def main(argv):
	parser = ArgumentParser(argv[0], description=__doc__)
	parser.add_argument('--num_components', '-c', type=int, default=20)
	parser.add_argument('--max_epochs',     '-e', type=int, default=4)
	parser.add_argument('--max_iter_tr',    '-m', type=int, default=5,
		help='Number of steps in the inner loop of the trust-region method.')

	args = parser.parse_args(argv[1:])

	experiment = Experiment()

	data = load('data/mnist.npz')['train']
	data = data[:, permutation(data.shape[1])]
	data = asarray(data, dtype=float) / 255.
	data = asarray(rand(*data.shape) < data, dtype=float, order='F')

	def callback(model):
		if model.num_updates * args.max_iter_tr % 25:
			return

		callback.num_updates.append(model.num_updates)
		callback.lower_bound.append(model.lower_bound(data))

		p = []
		for k in range(len(model)):
			p.append(model[k].alpha / (model[k].alpha + model[k].beta))
		p = hstack(p)

		imsave('results/mnist/mnist.{0}.png'.format(callback.counter),
			stitch(p.T.reshape(-1, 28, 28), num_rows=4), cmap='gray', vmin=0., vmax=1.)

		callback.counter += 1

	callback.counter = 0
	callback.num_updates = []
	callback.lower_bound = []

	os.system('rm -f results/mnist/mnist.*.png')

	try:
		model = MoBernoulli(dim=784, num_components=args.num_components)
		model.train(data,
			batch_size=200,
			max_epochs=args.max_epochs,
			max_iter_tr=args.max_iter_tr,
			tau=100.,
			callback=callback)
	except KeyboardInterrupt:
		pass

	experiment['args'] = args
	experiment['model'] = model
	experiment['num_updates'] = callback.num_updates
	experiment['lower_bound'] = callback.lower_bound
	experient.save('results/mnist/mnist.{0}.{1}.{{0}}.{{1}}.xpck'.format(
		args.num_components, args.max_iter_tr))

 	os.system('ffmpeg -r 25 -i results/mnist/mnist.%d.png -vcodec mjpeg -qscale 0 mnist.{0}.{1}.avi'.format(
		args.num_components, args.max_iter_tr))

	return 0



if __name__ == '__main__':
	sys.exit(main(sys.argv))
