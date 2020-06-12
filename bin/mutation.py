from utils import *

def err_model(name):
    raise ValueError('Model {} not supported'.format(name))

def get_model(args, seq_len, vocab_size,):
    if args.model_name == 'hmm':
        from hmmlearn.hmm import MultinomialHMM
        model = MultinomialHMM(
            n_components=args.dim,
            startprob_prior=1.0,
            transmat_prior=1.0,
            algorithm='viterbi',
            random_state=1,
            tol=0.01,
            verbose=True,
            params='ste',
            init_params='ste'
        )
    elif args.model_name == 'dnn':
        from language_model import DNNLanguageModel
        model = DNNLanguageModel(
            seq_len,
            vocab_size,
            embedding_dim=20,
            hidden_dim=args.dim,
            n_hidden=2,
            n_epochs=args.n_epochs,
            batch_size=args.batch_size,
            cache_dir='target/{}'.format(args.namespace),
            seed=args.seed,
            verbose=True,
        )
    elif args.model_name == 'lstm':
        from language_model import LSTMLanguageModel
        model = LSTMLanguageModel(
            seq_len,
            vocab_size,
            embedding_dim=20,
            hidden_dim=args.dim,
            n_hidden=2,
            n_epochs=args.n_epochs,
            batch_size=batch_size,
            cache_dir='target/{}'.format(args.namespace),
            seed=args.seed,
            verbose=True,
        )
    elif args.model_name == 'bilstm':
        from language_model import BiLSTMLanguageModel
        model = BiLSTMLanguageModel(
            seq_len,
            vocab_size,
            embedding_dim=20,
            hidden_dim=args.dim,
            n_hidden=2,
            n_epochs=args.n_epochs,
            batch_size=args.batch_size,
            cache_dir='target/{}'.format(args.namespace),
            seed=args.seed,
            verbose=True,
        )
    elif args.model_name == 'attention':
        from language_model import AttentionLanguageModel
        model = AttentionLanguageModel(
            seq_len,
            vocab_size,
            embedding_dim=20,
            hidden_dim=args.dim,
            n_hidden=4,
            n_epochs=args.n_epochs,
            batch_size=args.batch_size,
            cache_dir='target/{}'.format(args.namespace),
            seed=args.seed,
            verbose=True,
        )
    else:
        err_model(args.model_name)

    return model

def featurize_seqs(seqs, vocabulary):
    start_int = len(vocabulary) + 1
    end_int = len(vocabulary) + 2
    sorted_seqs = sorted(seqs.keys())
    X = np.concatenate([
        np.array([ start_int ] + [
            vocabulary[word] for word in seq
        ] + [ end_int ]) for seq in sorted_seqs
    ]).reshape(-1, 1)
    lens = np.array([ len(seq) + 2 for seq in sorted_seqs ])
    assert(sum(lens) == X.shape[0])
    return X, lens

def fit_model(name, model, seqs, vocabulary):
    X, lengths = featurize_seqs(seqs, vocabulary)
    model.fit(X, lengths)
    return model

def cross_entropy(logprob, n_samples):
    return -logprob / n_samples

def report_performance(model_name, model, vocabulary,
                       train_seqs, test_seqs):
    X_train, lengths_train = featurize_seqs(train_seqs, vocabulary)
    logprob = model.score(X_train, lengths_train)
    tprint('Model {}, train cross entropy: {}'
           .format(model_name, cross_entropy(logprob, len(lengths_train))))
    X_test, lengths_test = featurize_seqs(test_seqs, vocabulary)
    logprob = model.score(X_test, lengths_test)
    tprint('Model {}, test cross entropy: {}'
           .format(model_name, cross_entropy(logprob, len(lengths_test))))

def train_test(args, model, seqs, vocabulary, split_seqs=None):
    if args.train and args.train_split:
        raise ValueError('Training on full and split data is invalid.')

    if args.train:
        model = fit_model(args.model_name, model, seqs, vocabulary)
        return

    if split_seqs is None:
        raise ValueError('Must provide function to split train/test.')
    train_seqs, val_seqs = split_seqs(seqs)

    if args.train_split:
        model = fit_model(args.model_name, model, train_seqs, vocabulary)
    if args.test:
        report_performance(args.model_name, model, vocabulary,
                           train_seqs, val_seqs)

def embed_seqs(args, model, seqs, vocabulary,
               use_cache=False, verbose=True):
    X_cat, lengths = featurize_seqs(seqs, vocabulary)

    if use_cache:
        mkdir_p('target/{}/embedding'.format(args.namespace))
        embed_fname = ('target/{}/embedding/{}_{}.npy'
                       .format(args.namespace, args.model_name, args.dim))
    else:
        embed_fname = None

    if os.path.exists(embed_fname) and use_cache:
        X_embed = np.load(embed_fname)
    else:
        X_embed = model.transform(X_cat, lengths, embed_fname)
        if use_cache:
            np.save(embed_fname, X_embed)

    sorted_seqs = sorted(seqs)
    for seq_idx, seq in enumerate(sorted_seqs):
        for meta in seqs[seq]:
            meta['embedding'] = X_embed[seq_idx]

    return seqs

def predict_sequence_prob(args, seq_of_interest, vocabulary, model,
                          verbose=False):
    seqs = { seq_of_interest: [ {} ] }
    X_cat, lengths = featurize_seqs(seqs, vocabulary)

    y_pred = model.predict(X_cat, lengths)
    assert(y_pred.shape[0] == len(seq_of_interest) + 2)

    return y_pred

def analyze_semantics(args, model, vocabulary, seq_to_mutate, escape_seqs,
                      prob_cutoff=0., beta=1., plot_acquisition=True,
                      verbose=True,):
    if plot_acquisition:
        dirname = ('target/{}/semantics/cache'.format(args.namespace))
        mkdir_p(dirname)

    y_pred = predict_sequence_prob(
        args, seq_to_mutate, vocabulary, model, verbose=verbose
    )

    word_pos_prob = {}
    for i in range(len(seq_to_mutate)):
        for word in vocabulary:
            word_idx = vocabulary[word]
            prob = y_pred[i + 1, word_idx]
            word_pos_prob[(word, i)] = prob

    prob_sorted = sorted(word_pos_prob.items(), key=lambda x: -x[1])
    prob_seqs = { seq_to_mutate: [ {} ] }
    seq_prob = {}
    for (word, pos), prob in prob_sorted:
        mutable = seq_to_mutate[:pos] + word + seq_to_mutate[pos + 1:]
        seq_prob[mutable] = prob
        if prob >= prob_cutoff:
            prob_seqs[mutable] = [ {} ]

    seqs = np.array([ str(seq) for seq in sorted(seq_prob.keys()) ])

    if plot_acquisition:
        ofname = dirname + '/{}_mutations.txt'.format(args.namespace)
        with open(ofname, 'w') as of:
            of.write('orig\tmutant\n')
            for seq in seqs:
                try:
                    didx = [
                        c1 != c2 for c1, c2 in zip(seq_to_mutate, seq)
                    ].index(True)
                    of.write('{}\t{}\t{}\n'
                             .format(didx, seq_to_mutate[didx], seq[didx]))
                except ValueError:
                    of.write('NA\n')

    prob_seqs = embed_seqs(
        args, model, prob_seqs, vocabulary,
        use_cache=False, verbose=verbose
    )
    base_embedding = prob_seqs[seq_to_mutate][0]['embedding']
    seq_change = {}
    for seq in seqs:
        if seq in prob_seqs:
            embedding = prob_seqs[seq][0]['embedding']
            # L1 distance between embedding vectors.
            seq_change[seq] = abs(base_embedding - embedding).sum()
        else:
            seq_change[seq] = 0

    prob = np.array([ seq_prob[seq] for seq in seqs ])
    change = np.array([ seq_change[seq] for seq in seqs ])

    escape_idx = np.array([
        ((seq in escape_seqs) and
         (sum([ m['significant'] for m in escape_seqs[seq] ]) > 0))
        for seq in seqs
    ])
    viable_idx = np.array([ seq in escape_seqs for seq in seqs ])

    if plot_acquisition:
        cache_fname = dirname + ('/plot_{}_{}.npz'
                                 .format(args.model_name, args.dim))
        np.savez_compressed(
            cache_fname, prob=prob, change=change,
            escape_idx=escape_idx, viable_idx=viable_idx,
        )
        from cached_semantics import cached_escape_semantics
        cached_escape_semantics(cache_fname, beta,
                                plot=plot_acquisition,
                                namespace=args.namespace)

    return seqs, prob, change, escape_idx, viable_idx
