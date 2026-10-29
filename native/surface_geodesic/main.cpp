// Continuous shortest paths on a fixed triangular surface. CGAL implements the
// Xin-Wang/Chen-Han algorithm; EPICK uses double constructions and exact predicates.
#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/Surface_mesh.h>
#include <CGAL/Surface_mesh_shortest_path.h>
#include <CGAL/version.h>
#include <algorithm>
#include <array>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

using Kernel = CGAL::Exact_predicates_inexact_constructions_kernel;
using Mesh = CGAL::Surface_mesh<Kernel::Point_3>;
using Traits = CGAL::Surface_mesh_shortest_path_traits<Kernel, Mesh>;
using Solver = CGAL::Surface_mesh_shortest_path<Traits>;
using Weights = Traits::Barycentric_coordinates;
using Triangle = std::array<int, 3>;

struct Attachment {
  int triangle = -1, vertex = -1;
  std::array<double, 3> weights{};
};

struct Visitor {
  const Mesh& mesh;
  const std::vector<Triangle>& original;
  std::vector<Attachment> path;
  void operator()(Mesh::Vertex_index v) { Attachment a; a.vertex = v.idx(); path.push_back(a); }
  void operator()(Mesh::Halfedge_index h, double t) {
    auto f = mesh.face(h);
    if (f == Mesh::null_face()) f = mesh.face(mesh.opposite(h));
    Attachment a; a.triangle = f.idx();
    for (int i = 0; i < 3; ++i) {
      if (original[a.triangle][i] == int(mesh.source(h).idx())) a.weights[i] += 1-t;
      if (original[a.triangle][i] == int(mesh.target(h).idx())) a.weights[i] += t;
    }
    path.push_back(a);
  }
  void operator()(Mesh::Face_index f, Weights weights) {
    Attachment a; a.triangle = f.idx();
    auto h = mesh.halfedge(f);
    std::array<int, 3> order{int(mesh.source(h).idx()), int(mesh.target(h).idx()), int(mesh.target(mesh.next(h)).idx())};
    for (int i = 0; i < 3; ++i) for (int j = 0; j < 3; ++j)
      if (original[a.triangle][i] == order[j]) a.weights[i] = CGAL::to_double(weights[j]);
    path.push_back(a);
  }
};

Weights solver_weights(const Mesh& mesh, const std::vector<Triangle>& faces, const Attachment& a) {
  auto h = mesh.halfedge(Mesh::Face_index(a.triangle));
  std::array<int, 3> order{int(mesh.source(h).idx()), int(mesh.target(h).idx()), int(mesh.target(mesh.next(h)).idx())};
  Weights result{};
  for (int i = 0; i < 3; ++i) for (int j = 0; j < 3; ++j)
    if (order[i] == faces[a.triangle][j]) result[i] = a.weights[j];
  return result;
}

void output_attachment(const Attachment& a) {
  if (a.vertex >= 0) std::cout << "{\"kind\":\"vertex\",\"vertex_index\":" << a.vertex << '}';
  else std::cout << "{\"kind\":\"barycentric\",\"triangle_index\":" << a.triangle
    << ",\"weights\":[" << a.weights[0] << ',' << a.weights[1] << ',' << a.weights[2] << "]}";
}

int main(int argc, char** argv) {
  std::cout << std::setprecision(17);
  if (argc == 2 && std::string(argv[1]) == "--version") {
    std::cout << "{\"cgal_version\":\"" << CGAL_VERSION_STR << "\",\"method\":\"cgal_continuous_v1\"}\n";
    return 0;
  }
  try {
    int n, m, q;
    if (!(std::cin >> n >> m >> q) || n < 3 || n > 20000 || m < 1 || m > 40000 || q < 1 || q > 8)
      throw std::runtime_error("invalid_counts");
    Mesh mesh;
    for (int i = 0; i < n; ++i) {
      double x, y, z;
      if (!(std::cin >> x >> y >> z) || !std::isfinite(x) || !std::isfinite(y) || !std::isfinite(z))
        throw std::runtime_error("invalid_vertex");
      mesh.add_vertex({x, y, z});
    }
    std::vector<Triangle> faces(m);
    for (int i = 0; i < m; ++i) {
      auto& f = faces[i];
      if (!(std::cin >> f[0] >> f[1] >> f[2])) throw std::runtime_error("invalid_face");
      for (int v : f) if (v < 0 || v >= n) throw std::runtime_error("invalid_face_index");
      if (mesh.add_face(Mesh::Vertex_index(f[0]), Mesh::Vertex_index(f[1]), Mesh::Vertex_index(f[2])) == Mesh::null_face())
        throw std::runtime_error("mesh_not_consistently_oriented_manifold");
      if (CGAL::collinear(mesh.point(Mesh::Vertex_index(f[0])), mesh.point(Mesh::Vertex_index(f[1])), mesh.point(Mesh::Vertex_index(f[2]))))
        throw std::runtime_error("degenerate_triangle");
    }
    std::cout << "{\"method\":\"cgal_continuous_v1\",\"cgal_version\":\"" << CGAL_VERSION_STR
      << "\",\"arithmetic\":\"exact_predicates_double_constructions\",\"results\":[";
    for (int query = 0; query < q; ++query) {
      Attachment start, end;
      for (auto* a : {&start, &end}) {
        if (!(std::cin >> a->triangle >> a->weights[0] >> a->weights[1] >> a->weights[2]) || a->triangle < 0 || a->triangle >= m)
          throw std::runtime_error("invalid_endpoint");
        double sum = 0;
        for (double v : a->weights) {
          if (!std::isfinite(v) || v < 0 || v > 1) throw std::runtime_error("invalid_weights");
          sum += v;
        }
        if (std::abs(sum-1) > 1e-9) throw std::runtime_error("invalid_weights");
        for (double& v : a->weights) v /= sum;
      }
      Solver solver(mesh);
      solver.add_source_point(Mesh::Face_index(start.triangle), solver_weights(mesh, faces, start));
      Visitor visitor{mesh, faces, {}};
      auto result = solver.shortest_path_sequence_to_source_points(Mesh::Face_index(end.triangle), solver_weights(mesh, faces, end), visitor);
      if (query) std::cout << ',';
      if (result.first < 0) { std::cout << "{\"status\":\"disconnected\",\"length_mm\":null,\"path\":[]}"; continue; }
      std::reverse(visitor.path.begin(), visitor.path.end());
      // Retain the exact original face locations at both ends. CGAL may report
      // a vertex/edge instead when an endpoint lies on a triangle boundary.
      visitor.path.insert(visitor.path.begin(), start); visitor.path.push_back(end);
      std::cout << "{\"status\":\"ok\",\"length_mm\":" << result.first << ",\"path\":[";
      for (std::size_t i = 0; i < visitor.path.size(); ++i) { if (i) std::cout << ','; output_attachment(visitor.path[i]); }
      std::cout << "]}";
    }
    std::cout << "]}\n";
  } catch (const std::exception& error) {
    std::cerr << error.what() << '\n'; return 1;
  }
}
