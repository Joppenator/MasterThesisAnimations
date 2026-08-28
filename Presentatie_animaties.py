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


class C5ToUmbrella(ThreeDScene):
	def construct(self):
		graph_radius = 3.0
		graph_angles = [90, 18, -54, -126, 162]
		graph_positions = [
			graph_radius * np.array([
				 np.cos(angle * DEGREES),
				 np.sin(angle * DEGREES),
				 0,
			])
			for angle in graph_angles
		]

		self.set_camera_orientation(phi=0, theta=-90 * DEGREES)
		vertices = VGroup()
		labels = VGroup()
		for index, position in enumerate(graph_positions):
			vertices.add(Circle(radius=0.48, color=BLACK).move_to(position))
			labels.add(MathTex(str(index), color=BLACK).move_to(position))

		edges = VGroup(*[
			Line(
				graph_positions[index],
				graph_positions[(index + 1) % 5],
				buff=0.48,
				stroke_width=4,
				color=BLACK,
			)
			for index in range(5)
		])
		# title = Text("The cycle graph C_5", font_size=30, color=BLACK).to_edge(UP)

		self.play(Create(edges), Create(vertices), Write(labels))
		self.wait(1)
		self.play(FadeOut(edges), run_time=1)

		canopy_center = np.array([0, 0, 1.15])
		rim_radius = 3.0
		rim_z = 0.3
		rim_positions = [
			rim_radius * np.array([
				 np.cos(angle * DEGREES),
				 np.sin(angle * DEGREES),
				 0,
			]) + np.array([0, 0, rim_z])
			for angle in graph_angles
		]
		ribs = VGroup(*[
			Line(canopy_center, position, stroke_width=5, color=BLACK)
			for position in rim_positions
		])

		self.play(
			*[ReplacementTransform(vertex, rib) for vertex, rib in zip(vertices, ribs)],
			*[Transform(label, label.copy().move_to(position))
			  for label, position in zip(labels, rim_positions)],
			run_time=2,
		)
		self.move_camera(phi=65 * DEGREES, theta=-55 * DEGREES, run_time=2)

		canopy = Surface(
			lambda u, v: np.array([
				v * np.cos(u),
				v * np.sin(u),
				canopy_center[2] - 0.85 * (v / rim_radius) ** 2,
			]),
			u_range=[0, TAU],
			v_range=[0, rim_radius],
			resolution=(32, 8),
			fill_color=GREY_B,
			fill_opacity=0.22,
			stroke_color=BLACK,
			stroke_opacity=0.35,
		)
		canopy.set_shade_in_3d(True)

		handle_shaft = Line(
			[0, 0, canopy_center[2]],
			[0, 0, -2.6],
			stroke_width=6,
			color=BLACK,
		)
		handle_hook = ParametricFunction(
			lambda parameter: np.array([
				0.65 - 0.65 * np.cos(parameter),
				0,
				-2.6 - 0.65 * np.sin(parameter),
			]),
			t_range=[0, PI],
			color=BLACK,
			stroke_width=6,
		)
		self.play(Create(canopy), Create(handle_shaft), Create(handle_hook), run_time=2)
		self.begin_ambient_camera_rotation(rate=0.08)
		self.wait(4)
		self.stop_ambient_camera_rotation()


class ExtendHatchedSquare(Scene):
	def construct(self):
		cell_size = 0.82
		slow_factor = 1.5
		final_bottom_left = LEFT * 3.5 * cell_size + DOWN * 3.5 * cell_size

		def cell(row, column, hatch_column=None):
			center = final_bottom_left + RIGHT * (column + 0.5) * cell_size
			center += UP * (row + 0.5) * cell_size
			cell_shape = Rectangle(
				width=cell_size,
				height=cell_size,
				stroke_width=3,
				stroke_color=BLACK,
				fill_color=WHITE,
				fill_opacity=1,
			).move_to(center)

			hatched_columns = {0: 2, 1: 4, 2: 1, 3: 3, 4: 0}
			if hatch_column is None:
				source_row = min(row, 4)
				hatch_column = 2 + hatched_columns[4 - source_row]
			if column != hatch_column:
				return VGroup(cell_shape)

			hatches = VGroup()
			half_cell = cell_size / 2
			for offset in np.linspace(-0.7, 0.7, 18):
				start_x = max(-half_cell, -half_cell - offset)
				end_x = min(half_cell, half_cell - offset)
				hatches.add(
					Line(
						center + RIGHT * start_x + UP * (start_x + offset),
						center + RIGHT * end_x + UP * (end_x + offset),
						stroke_width=2,
						color=BLACK,
					)
				)
			return VGroup(cell_shape, hatches)

		def row(row_index, start_column=2):
			return VGroup(*[
				cell(row_index, column)
				for column in range(start_column, start_column + 5)
			])

		def empty_block(row_index, column):
			center = final_bottom_left + RIGHT * (column + 1) * cell_size
			center += UP * (row_index + 1) * cell_size
			return Rectangle(
				width=2 * cell_size,
				height=2 * cell_size,
				stroke_width=3,
				stroke_color=BLACK,
				fill_color=WHITE,
				fill_opacity=1,
			).move_to(center)

		# The original board is placed at the lower-right of the final board.
		original_rows = [row(row_index) for row_index in range(5)]
		original = VGroup(*original_rows)
		self.play(
			LaggedStart(*[Create(board_row) for board_row in original_rows]),
			run_time=2 * slow_factor,
		)
		empty_blocks = [empty_block(3, 2), empty_block(2,4), empty_block(1, 1), empty_block(0,3), empty_block(4, 0)]
		for i in range(len(empty_blocks)):
			self.play(Create(empty_blocks[i]), run_time=1 * slow_factor)
		self.wait(0.5 * slow_factor)

		top_row = original_rows[-1]
		top_highlight = SurroundingRectangle(
			top_row,
			buff=0.04,
			color=YELLOW,
			stroke_width=7,
		)
		self.play(
			Create(top_highlight),
			Indicate(top_row, color=YELLOW),
			run_time=1 * slow_factor,
		)

		new_top_rows = []
		for row_index in (5, 6):
			new_row = row(row_index)
			self.play(TransformFromCopy(top_row, new_row), run_time=1 * slow_factor)
			new_top_rows.append(new_row)
			new_block = empty_block(row_index - 2, 2)
			self.play(Create(new_block), run_time=1 * slow_factor)
			empty_blocks.append(new_block)
		self.play(FadeOut(top_highlight), run_time=1 * slow_factor)

		expanded_rows = original_rows + new_top_rows
		left_column = VGroup(*[board_row[0] for board_row in expanded_rows])
		left_highlight = SurroundingRectangle(
			left_column,
			buff=0.04,
			color=YELLOW,
			stroke_width=7,
		)
		self.play(
			Create(left_highlight),
			Indicate(left_column, color=YELLOW),
			run_time=1 * slow_factor,
		)

		for column in (1, 0):
			new_column = VGroup(*[
				cell(row_index, column, hatch_column=column if row_index == 0 else -1)
				for row_index in range(7)
			])
			self.play(TransformFromCopy(left_column, new_column), run_time=1 * slow_factor)
			left_column = new_column
			new_block = empty_block(3, column)
			self.play(Create(new_block), run_time=1 * slow_factor)
			empty_blocks.append(new_block)
		self.play(FadeOut(left_highlight), run_time=1 * slow_factor)
		self.wait(2 * slow_factor)

