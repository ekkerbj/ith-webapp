# src/ith_webapp/services/service_follow_up_chain.py

SERVICE_FOLLOW_UP_STAGES = [
    "Follow Up",
    "Follow UpA",
    "Follow UpB",
    "Follow UpC",
    "Follow Up1",
    "Follow Up2",
    "Follow Up3",
    "Follow Up4",
    "Follow Up5",
]

def get_service_stage(service):
    if not hasattr(service, "_follow_up_stage_index"):
        return SERVICE_FOLLOW_UP_STAGES[0]
    idx = getattr(service, "_follow_up_stage_index", 0)
    return SERVICE_FOLLOW_UP_STAGES[idx]

def advance_service_stage(service):
    idx = getattr(service, "_follow_up_stage_index", 0)
    if idx < len(SERVICE_FOLLOW_UP_STAGES) - 1:
        idx += 1
    setattr(service, "_follow_up_stage_index", idx)
