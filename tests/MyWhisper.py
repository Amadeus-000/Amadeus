import torch
import torch.nn.functional as F
from torch import Tensor
from torch.distributions import Categorical
import whisper

# python3.9以上じゃないと動かない
# whisperのupdate関数を変更して、特定の単語の出現を促す

multiply_coef = 1.2

def create_hints(tokenizer, hints:list[str], hints_bad:list[str]) -> tuple[list[int], list[int]]:
    hints_id = [tokenizer.encode(hint) for hint in hints]
    hints_bad_id = [tokenizer.encode(hint) for hint in hints_bad]
    return hints_id, hints_bad_id


def update(self, tokens: Tensor, logits: Tensor, sum_logprobs: Tensor) -> tuple[Tensor, bool]:
    def update_logits(hints_id, multiply_coef):
        for hint_ids in hints_id:
            reverse_hint_ids = hint_ids[::-1]
            for i, hint_id in enumerate(reverse_hint_ids):
                skip = False
                for y, previous_id in enumerate(reverse_hint_ids[i+1:]):
                    if tokens[0][-(y+1)] != previous_id:
                        skip=True
                        break
                if not skip:
                    logits[0][hint_id] *= multiply_coef
                    break
    
    update_logits(hints_id, multiply_coef)
    update_logits(hints_bad_id, 1/multiply_coef)

    if self.temperature == 0:
        next_tokens = logits.argmax(dim=-1)
    else:
        next_tokens = Categorical(logits=logits / self.temperature).sample()

    logprobs = F.log_softmax(logits.float(), dim=-1)
    current_logprobs = logprobs[torch.arange(logprobs.shape[0]), next_tokens]
    sum_logprobs += current_logprobs * (tokens[:, -1] != self.eot)

    next_tokens[tokens[:, -1] == self.eot] = self.eot
    tokens = torch.cat([tokens, next_tokens[:, None]], dim=-1)

    completed = (tokens[:, -1] == self.eot).all()
    return tokens, completed

whisper.decoding.GreedyDecoder.update = update#既存の関数を変更

# Now you can use the customized GreedyDecoder in your transcribe function
device: str = "cuda" if torch.cuda.is_available() else "cpu"
sample_file_path: str = "downloads/sample5.wav"
model = whisper.load_model("large-v2", device=device)
tokenizer = whisper.tokenizer.get_tokenizer(True, language="ja", task="asr")
hints_id, hints_bad_id = create_hints(tokenizer, ['自慰行為','精液','前立腺','ザーメン'], ['座面'])
result = model.transcribe(
    sample_file_path,
    language='ja',
    )
print("認識結果", result["text"])