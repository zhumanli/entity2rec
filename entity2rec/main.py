from entity2rec import Entity2Rec
from evaluator import Evaluator
import time
from parse_args import parse_args
import numpy as np

np.random.seed(1)  # fixed seed for reproducibility

start_time = time.time()

print('Starting entity2rec...')

args = parse_args()

if not args.train:
    args.train = 'datasets/'+args.dataset+'/train.dat'

if not args.test:
    args.test = 'datasets/'+args.dataset+'/test.dat'

if not args.validation:
    args.validation = 'datasets/'+args.dataset+'/val.dat'


# initialize entity2rec recommender
e2rec = Entity2Rec(args.dataset, run_all=args.run_all, p=args.p, q=args.q,
                   feedback_file=args.feedback_file, walk_length=args.walk_length,
                   num_walks=args.num_walks, dimensions=args.dimensions, window_size=args.window_size,
                   workers=args.workers, iterations=args.iter, collab_only=args.collab_only,
                   content_only=args.content_only)

# initialize evaluator

evaluat = Evaluator(implicit=args.implicit, threshold=args.threshold, all_unrated_items=args.all_unrated_items)

# compute e2rec features
x_train, y_train, qids_train, x_test, y_test, qids_test,\
x_val, y_val, qids_val = evaluat.features(e2rec, args.train, args.test,
                                          validation=args.validation, n_users=args.num_users, n_jobs=args.workers)

print('Finished computing features after %s seconds' % (time.time() - start_time))
print('Starting to fit the model...')

# fit e2rec on features
e2rec.fit(x_train, y_train, qids_train,
          x_val=x_val, y_val=y_val, qids_val=qids_val, optimize=args.metric, N=args.N)  # train the model

print('Finished fitting the model after %s seconds' % (time.time() - start_time))

evaluat.evaluate(e2rec, x_test, y_test, qids_test)  # evaluates the recommender on the test set

evaluat.evaluate_heuristics(x_test, y_test, qids_test)  # evaluates the heuristics on the test set

print("--- %s seconds ---" % (time.time() - start_time))

with open('features.svm', 'w') as feature_file:

    for i, x_train in enumerate(x_train):

        for j, f in enumerate(x_train):

            feature_file.write('%f,' % f)

        feature_file.write('%f\n' % y_train[i])
