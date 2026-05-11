# Recommendation Reflection

## High-Energy Pop vs Chill Lofi

High-Energy Pop prefers happy songs with high energy and electronic production. The top recommendations are bright and danceable, which matches the profile well.

Chill Lofi shifts toward softer, low-energy, and acoustic tracks. The recommended songs are more relaxed and mellow, showing that the system can distinguish between energetic and calm taste profiles.

## Deep Intense Rock vs Sad Energy Conflict

Deep Intense Rock selects intense songs that are also energetic and danceable. It tends to choose tracks that feel powerful.

Sad Energy Conflict still tries to satisfy the high energy request, but it is limited by the small dataset of sad songs. That means the model may produce partially sad or higher-energy songs because a perfect sad/high-energy match is rare.

## Experiment: Mood Ignored

When mood scoring is ignored, the system relies more on energy and acoustic preference. The top songs become more consistently energetic, but they may feel less emotionally right for the profile. This demonstrates that mood matching is important for keeping recommendations aligned with user intent.

## Reliability Testing

I added a synthetic reliability harness for natural-language requests. It checks whether the top recommendation aligns with the requested mood and listening context, and whether the confidence score is above an expected threshold. This exposed cases where the catalog is too small to support exact matches and helped justify the mood-first fallback behavior for stronger results.

## Biases and Misuse Prevention

The system is biased by the limited song catalog and the predefined mood/genre labels. It can over-recommend popular happy tracks and under-represent niche moods or less common genres. Because the recommendation logic emphasizes energy and mood matching, it may also fail when user requests mix conflicting signals like "sad but powerful workout music." 

To reduce misuse, the system is explicitly documented as a prototype for learning and experimentation only. It is not presented as a production-grade music service, and it avoids claiming human-level judgment or objective taste. The README and model card both state that the dataset is small, recommendations are explainable, and real-world systems need more data, personalization history, and fairness checks.

## AI Collaboration Story

During development, AI assistance was useful for suggesting an agentic architecture and helping phrase reflection text clearly. One helpful suggestion was to separate the system into parser, retriever, scorer, and validator stages, which made the design much easier to explain. A flawed suggestion occurred when the early prompt generation advice pushed toward a too-complex confidence calculation; I simplified it to a reliable, interpretable score based only on mood/context alignment.

This collaboration shows that AI can accelerate architecture design and documentation, but the final system still needs human oversight to keep the logic grounded and the ethics explicit.