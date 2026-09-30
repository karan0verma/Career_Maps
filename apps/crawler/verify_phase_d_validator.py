import json
from src.validators.job_validator import JobValidator
from src.discovery.models import Target
from src.dto.job_normalized_dto import JobNormalizedDTO

def make_job(title, applyUrl="", externalJobId="", location=None, employmentType=None, desc=""):
    return JobNormalizedDTO(
        companyId="1", companyName="Test", title=title, 
        externalJobId=externalJobId, applyUrl=applyUrl, sourceATS="A",
        description=desc, location=location, city=None, state=None, country=None, 
        employmentType=employmentType, experience=None
    )

def run_tests():
    validator = JobValidator()
    
    print("--- Testing Phase D Validator ---")
    
    # 1. Valid Job (KNOWN_ATS)
    t_ats = Target(company_name="Test", domain="test.com", career_url="", extraction_strategy="KNOWN_ATS")
    j1 = make_job(title="Software Engineer", externalJobId="123", applyUrl="https://t/1")
    v1, r1, d1 = validator.process(t_ats, [j1])
    assert len(v1) == 1, "Valid job should be accepted for KNOWN_ATS"
    print("[x] Valid job accepted")
    
    # 2. Non-Job Title (Blog)
    j_blog = make_job(title="Engineering Blog", applyUrl="https://t/blog")
    v2, r2, d2 = validator.process(t_ats, [j_blog])
    assert len(v2) == 0, "Blog should be rejected"
    assert r2[0]['reasons'][0] == "Title contains strong non-job keywords"
    print("[x] Blog keyword rejected")
    
    # 3. Exact Non-Job Title (About Us)
    j_about = make_job(title="About Us", applyUrl="https://t/about")
    v3, r3, d3 = validator.process(t_ats, [j_about])
    assert len(v3) == 0, "About us should be rejected"
    assert "blacklist" in r3[0]['reasons'][0]
    print("[x] Exact blacklist keyword rejected")
    
    # 4. GENERIC_DOM strictness
    t_dom = Target(company_name="Test", domain="test.com", career_url="", extraction_strategy="GENERIC_DOM")
    j_weak = make_job(title="Random Role", applyUrl="https://t/random")
    v4, r4, d4 = validator.process(t_dom, [j_weak])
    assert len(v4) == 0, "Weak generic dom job should be rejected"
    assert "below threshold" in r4[0]['reasons'][0]
    print("[x] Generic DOM weak signal rejected")
    
    j_strong = make_job(title="Senior Software Engineer", applyUrl="https://t/job/123", externalJobId="123", location="NY", employmentType="Full time", desc="x" * 60)
    v5, r5, d5 = validator.process(t_dom, [j_strong])
    assert len(v5) == 1, f"Strong generic dom job should be accepted, but got: {r5}"
    print("[x] Generic DOM strong signal accepted")
    
    # 5. Duplicates
    v6, r6, d6 = validator.process(t_ats, [
        make_job(title="Dev", externalJobId="1", applyUrl="https://t/1"),
        make_job(title="Dev 2", externalJobId="1", applyUrl="https://t/2")
    ])
    assert len(v6) == 1, "Duplicate externalId should be removed"
    assert d6 == 1, "Should count 1 duplicate"
    print("[x] Deduplication works")

if __name__ == "__main__":
    run_tests()
    print("All validator unit tests passed!")
