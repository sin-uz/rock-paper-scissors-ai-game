import time, math
from collections import defaultdict
#discussions: ignore small jitters completely if dx<TH -> dx=0

class BaseFilter:
  def __init__(self, timeout=0.5, n_landmarks=21):
    self.timeout = timeout #for forgetting state
    self.n_landmarks = n_landmarks

    self._filters = {"Left": None, "Right": None}
    self._last_seen = {"Left": 0.0, "Right": 0.0}

  def check_seen(self):
    now = time.perf_counter()

    for side in ["Left", "Right"]:
      if now - self._last_seen.get(side, 0) > self.timeout:
        #we reset last filter state if hand disappears
        #so the new one isnt affected by the old state
        self._filters[side] = None

    return now

  def smoothen(self, side, landmarks, now=None):
    if now is None:
      now = time.perf_counter()

    self._last_seen[side] = now

    if self._filters[side] is None:
      self._filters[side] = self._init_filters()

    filters = self._filters[side]

    smoothed = []
    #apparently gpt knows issues other people had, and insists on
    # Why per-landmark works
    # Each landmark:
    # has its own velocity
    # gets its own adaptive cutoff
    # is smoothed appropriately
    # Example:
    # wrist steady -> strong smoothing
    # fingertip moving -> low smoothing (responsive)
    for i, (x, y, z) in enumerate(landmarks):
      smoothed.append(
        self._smooth_point(filters[i], x, y, z, now)
      )

    return smoothed

  #base filter wont run xd
  def _init_filters(self):
    raise NotImplementedError

  def _smooth_point(self, state, x, y, z, t):
    raise NotImplementedError

class OneEuroFilter(BaseFilter):
  def __init__(self, min_cutoff=1.0, beta=0.01, d_cutoff=1.0, **kwargs):
    #GPT:
    # min_cutoff = 1.0   # more smoothing -> increase
    # beta       = 0.01  # more responsiveness -> increase
    # d_cutoff   = 1.0

    # Tune like this:
    # jittery when still -> increase min_cutoff  (actually lower cutoff = more smoothing, so decrease value)
    # too laggy -> increase beta
    super().__init__(**kwargs)
    self.min_cutoff = min_cutoff
    self.beta = beta
    self.d_cutoff = d_cutoff

  def _init_filters(self):
    # one state per landmark
    return [self._make_state() for _ in range(self.n_landmarks)]

  def _make_state(self):
    return {
        "x_prev": None,
        "dx_prev": 0.0,
        "t_prev": None
    }

  def _alpha(self, cutoff, dt):
    tau = 1.0 / (2 * math.pi * cutoff)
    return 1.0 / (1.0 + tau / dt)

  def _filter_scalar(self, state, x, t):
    if state["t_prev"] is None:
      state["t_prev"] = t
      state["x_prev"] = x
      return x

    dt = t - state["t_prev"]
    if dt <= 0:
      return x

    dx = (x - state["x_prev"]) / dt
    alpha_d = self._alpha(self.d_cutoff, dt)
    dx_hat = alpha_d * dx + (1 - alpha_d) * state["dx_prev"]

    cutoff = self.min_cutoff + self.beta * abs(dx_hat)
    alpha = self._alpha(cutoff, dt)
    
    #seems its just adaptive weighted decay
    x_hat = alpha * x + (1 - alpha) * state["x_prev"]

    state["x_prev"] = x_hat
    state["dx_prev"] = dx_hat
    state["t_prev"] = t

    return x_hat

  def _smooth_point(self, state, x, y, z, t):
    return (
      self._filter_scalar(state.setdefault("x", {}), x, t),
      self._filter_scalar(state.setdefault("y", {}), y, t),
      self._filter_scalar(state.setdefault("z", {}), z, t),
    )

class SimpleFilter(BaseFilter):
  def __init__(self, alpha=0.9, **kwargs):
    super().__init__(**kwargs)
    self.alpha = alpha

  def _init_filters(self):
    # one state per landmark
    return [self._make_state() for _ in range(self.n_landmarks)]

  def _make_state(self):
    return {
      "x_prev": None
    }

  def _filter_scalar(self, state, x):
    if state["x_prev"] is None:
      state["x_prev"] = x
      return x
    
    x_hat = self.alpha * x + (1 - self.alpha) * state["x_prev"]
    state["x_prev"] = x_hat

    return x_hat

  def _smooth_point(self, state, x, y, z, t):
    return (
      self._filter_scalar(state.setdefault("x", {}), x),
      self._filter_scalar(state.setdefault("y", {}), y),
      self._filter_scalar(state.setdefault("z", {}), z),
    )

class NoFilter(BaseFilter):
  def __init__(self, alpha=0.9, **kwargs):
    super().__init__(**kwargs)
    self.alpha = alpha

  def _init_filters(self):
    pass

  def smoothen(self, side, landmarks, now=None):
    return landmarks
