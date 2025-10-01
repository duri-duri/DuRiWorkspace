from duri_finale.phase_25_creative_collaboration_system import (
    CreativeCollaborationSystem,
)
from duri_finale.phase_25_ethical_judgment_system import EthicalJudgmentSystem
from duri_finale.phase_25_final_evolution_ai import FinalEvolutionAI
from duri_finale.phase_25_future_design_system import FutureDesignSystem


def boot():
    cc = CreativeCollaborationSystem()
    ej = EthicalJudgmentSystem()
    fd = FutureDesignSystem()
    fe = FinalEvolutionAI()

    # 각 클래스에 ready()/health()가 없다면 True 반환으로 대체
    def ok(x):
        return True if not hasattr(x, "ready") else bool(x.ready())

    return {
        "creative": ok(cc),
        "ethics": ok(ej),
        "future": ok(fd),
        "evolution": ok(fe),
    }


if __name__ == "__main__":
    print(boot())
