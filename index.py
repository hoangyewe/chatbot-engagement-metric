import time
import random
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Tuple

class MessageLength(Enum):
    SHORT = 1
    MEDIUM = 2
    LONG = 3

@dataclass
class Message:
    content: str
    timestamp: float
    is_user: bool
    length: MessageLength

class ChatbotEngagementMetrics:
    def __init__(self):
        self.messages: List[Message] = []
        self.page_switches: int = 0
        self.slow_responses: int = 0
        self.external_clicks: int = 0
        self.ghosting_time: float = 0
        self.last_bot_response_time: Optional[float] = None

    def add_message(self, content: str, is_user: bool):
        length = self._categorize_length(content)
        self.messages.append(Message(content, time.time(), is_user, length))

        if not is_user:
            self.last_bot_response_time = time.time()

    def record_page_switch(self):
        if self.last_bot_response_time and time.time() - self.last_bot_response_time < 5:
            self.page_switches += 1

    def record_slow_response(self):
        if len(self.messages) >= 2:
            time_diff = self.messages[-1].timestamp - self.messages[-2].timestamp
            if time_diff > 30:  # If user takes more than 30 seconds to respond
                self.slow_responses += 1

    def record_external_click(self):
        self.external_clicks += 1

    def update_ghosting_time(self):
        if self.messages and not self.messages[-1].is_user:
            self.ghosting_time += time.time() - self.messages[-1].timestamp

    def get_engagement_score(self) -> float:
        if len(self.messages) < 6:
            return 0.0

        total_messages = len(self.messages)
        user_messages = sum(1 for msg in self.messages if msg.is_user)
        avg_response_time = self._calculate_avg_response_time()

        engagement_score = (
            (user_messages / total_messages) * 0.3 +
            (1 - (self.page_switches / total_messages)) * 0.2 +
            (1 - (self.slow_responses / user_messages)) * 0.2 +
            (1 - (self.external_clicks / total_messages)) * 0.2 +
            (1 - min(self.ghosting_time / 300, 1)) * 0.1 
        )

        return min(max(engagement_score, 0), 1) 

    def _categorize_length(self, content: str) -> MessageLength:
        word_count = len(content.split())
        if word_count < 5:
            return MessageLength.SHORT
        elif word_count < 20:
            return MessageLength.MEDIUM
        else:
            return MessageLength.LONG

    def _calculate_avg_response_time(self) -> float:
        response_times = []
        for i in range(1, len(self.messages)):
            if self.messages[i].is_user != self.messages[i-1].is_user:
                response_times.append(self.messages[i].timestamp - self.messages[i-1].timestamp)
        return sum(response_times) / len(response_times) if response_times else 0

    def print_metrics(self):
        print(f"Total messages: {len(self.messages)}")
        print(f"Page switches: {self.page_switches}")
        print(f"Slow responses: {self.slow_responses}")
        print(f"External clicks: {self.external_clicks}")
        print(f"Ghosting time: {self.ghosting_time:.2f} seconds")
        print(f"Engagement score: {self.get_engagement_score():.2f}")

def generate_message(is_user: bool) -> Tuple[str, MessageLength]:
    lengths = [MessageLength.SHORT, MessageLength.MEDIUM, MessageLength.LONG]
    length = random.choice(lengths)
    
    if length == MessageLength.SHORT:
        word_count = random.randint(1, 4)
    elif length == MessageLength.MEDIUM:
        word_count = random.randint(5, 19)
    else:
        word_count = random.randint(20, 50)
    
    message = " ".join(["word" for _ in range(word_count)])
    return message, length

def simulate_conversation(duration: int = 300) -> ChatbotEngagementMetrics:
    metrics = ChatbotEngagementMetrics()
    start_time = time.time()
    is_user_turn = False

    while time.time() - start_time < duration:
        message, length = generate_message(is_user_turn)
        metrics.add_message(message, is_user_turn)

        if is_user_turn:
            # Simulate user behaviors
            if random.random() < 0.1:  # 10% chance of slow response
                metrics.record_slow_response()
            if random.random() < 0.05:  # 5% chance of page switch
                metrics.record_page_switch()
            if random.random() < 0.03:  # 3% chance of external click
                metrics.record_external_click()
        else:
            # Simulate bot behaviors
            if random.random() < 0.02:  # 2% chance of bot ghosting
                time.sleep(random.uniform(10, 60))
                metrics.update_ghosting_time()

        is_user_turn = not is_user_turn
        time.sleep(random.uniform(1, 10))  # Random delay between messages

    return metrics

def generate_dataset(num_conversations: int) -> List[ChatbotEngagementMetrics]:
    dataset = []
    for _ in range(num_conversations):
        metrics = simulate_conversation()
        dataset.append(metrics)
    return dataset

def analyze_dataset(dataset: List[ChatbotEngagementMetrics]):
    total_score = 0
    high_engagement = 0
    medium_engagement = 0
    low_engagement = 0

    for metrics in dataset:
        score = metrics.get_engagement_score()
        total_score += score

        if score > 0.7:
            high_engagement += 1
        elif score > 0.4:
            medium_engagement += 1
        else:
            low_engagement += 1

    avg_score = total_score / len(dataset)

    print(f"Dataset Analysis:")
    print(f"Total conversations: {len(dataset)}")
    print(f"Average engagement score: {avg_score:.2f}")
    print(f"High engagement conversations: {high_engagement}")
    print(f"Medium engagement conversations: {medium_engagement}")
    print(f"Low engagement conversations: {low_engagement}")

num_conversations = 100
dataset = generate_dataset(num_conversations)
analyze_dataset(dataset)


for i, metrics in enumerate(dataset[:5]):
    print(f"\nDetailed metrics for conversation {i+1}:")
    metrics.print_metrics()