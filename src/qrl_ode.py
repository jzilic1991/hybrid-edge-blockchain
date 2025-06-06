import mdptoolbox

from mdp_ode import MdpOde


class QrlOde(MdpOde):
    """Q-learning offloading decision engine built on top of MdpOde."""

    def _run_policy(cls, task, metrics, validity_vector):
        cls._update_P_matrix()
        cls._update_R_matrix(task, metrics, validity_vector)

        ql = mdptoolbox.mdp.QLearning(cls._P, cls._R, cls._discount_factor)
        ql.verbose = False
        ql.run()
        return ql.policy
