from manim import *

config.background_color = WHITE


class BipartiteToUndirected(Scene):
	def construct(self):
		capital_positions = {
			"A": LEFT * 4 + UP * 2.25,
			"B": LEFT * 4 + UP * 0.75,
			"C": LEFT * 4 + DOWN * 0.75,
			"D": LEFT * 4 + DOWN * 2.25,
		}
		lower_positions = {
			"a": RIGHT * 3 + UP * 2.25,
			"b": RIGHT * 3 + UP * 0.75,
			"c": RIGHT * 3 + DOWN * 0.75,
			"d": RIGHT * 3 + DOWN * 2.25,
		}

		def vertex(position, label):
			return MathTex(label, color=BLACK).move_to(position)

		capital_vertices = VGroup(
			*(vertex(position, label) for label, position in capital_positions.items())
		)
		lower_vertices = VGroup(
			*(vertex(position, label) for label, position in lower_positions.items())
		)

		directed_edges = VGroup()
		for source, target in (
			("A", "a"), ("A", "b"), ("B", "b"), ("C", "b"),
			("C", "c"), ("C", "d"), ("D", "d"),
		):
			start = capital_positions.get(source, lower_positions.get(source))
			end = capital_positions.get(target, lower_positions.get(target))
			directed_edges.add(
				Arrow(
					start,
					end,
					buff=0.35,
					stroke_width=4,
					max_tip_length_to_length_ratio=0.15,
					color=BLACK,
				)
			)

		title = Text("Communication channel", font_size=30, color=BLACK).to_edge(UP)
		self.play(Write(title), Write(capital_vertices))
		self.play(LaggedStart(*[Write(vertex) for vertex in lower_vertices]))
		self.play(LaggedStart(*[Create(edge) for edge in directed_edges]))
		self.wait(1)

		final_positions = {
			"A": LEFT * 2.2 + UP * 1.8,
			"B": RIGHT * 2.2 + UP * 1.8,
			"C": LEFT * 2.2 + DOWN * 1.8,
			"D": RIGHT * 2.2 + DOWN * 1.8,
		}
		final_vertices = VGroup(
			*(vertex(position, label) for label, position in final_positions.items())
		)
		undirected_edges = VGroup()
		for source, target in (("A", "B"), ("A", "C"), ("B", "C"), ("C", "D")):
			undirected_edges.add(
				Line(
					final_positions[source],
					final_positions[target],
					buff=0.35,
					stroke_width=5,
					color=BLACK,
				)
			)

		new_title = Text("Confusability graph", font_size=30, color=BLACK).to_edge(UP)
		self.play(
			FadeOut(directed_edges),
			FadeOut(lower_vertices),
			Transform(capital_vertices, final_vertices),
			Transform(title, new_title),
			run_time=2,
		)
		self.play(LaggedStart(*[Create(edge) for edge in undirected_edges]))
		self.wait(2)
