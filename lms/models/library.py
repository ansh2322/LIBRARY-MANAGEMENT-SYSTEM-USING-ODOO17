from lib2to3.fixes.fix_input import context

from odoo import models, fields, api


class BookDetail(models.Model):
    _name = "library.book.detail"
    _description = "Book Detail"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Book Title', required=True)
    author = fields.Char(string='Author', required=True)
    status = fields.Selection(string='Status', selection=[('available', 'Available'), ('reserved', 'Reserved'), ],
                              required=True, )
    transaction_ids = fields.One2many(comodel_name='library.transactions', inverse_name='book_id',
                                      string='Transactions', )
    chatter = fields.Text(string='Chatter', track_visibility='onchange', track_sequence=5)

    def print_book_details(self):
        return self.env.ref('lms.action_report_book_details').report_action(self)


class LibrarianDetail(models.Model):
    _name = 'librarian.detail'
    _description = 'Librarian Detail'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True)
    role = fields.Selection([('librarian', 'Librarian')], string='Role', required=True, default='librarian',
                            readonly=True)
    chatter = fields.Text(string='Chatter', track_visibility='onchange', track_sequence=5)

    transaction_count = fields.Integer(string='Transaction Count', compute='_compute_transaction_count', store=True, )

    transaction_ids = fields.One2many(comodel_name='library.transactions', inverse_name='person_id',
                                      string='Transactions', )

    def _compute_transaction_count(self):
        for librarian in self:
            librarian.transaction_count = len(librarian.transaction_ids)

    def print_librarian_details(self):
        return self.env.ref('lms.action_report_librarian_details').report_action(self)


class StudentDetail(models.Model):
    _name = 'student.detail'
    _description = 'Student Detail'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True)
    role = fields.Selection([('student', 'Student')], string='Role', required=True, default='student', readonly=True)
    chatter = fields.Text(string='Chatter', track_visibility='onchange', track_sequence=5)

    transaction_count = fields.Integer(string='Transaction Count', compute='_compute_transaction_count', store=True, )

    transaction_ids = fields.One2many(comodel_name='library.transactions', inverse_name='student_id',
                                      string='Transactions', )

    def _compute_transaction_count(self):
        for student in self:
            student.transaction_count = len(student.transaction_ids)

    def print_student_details(self):
        return self.env.ref('lms.action_report_student_details').report_action(self)


class Transactions(models.Model):
    _name = 'library.transactions'
    _description = 'Transactions'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    status = fields.Selection(
        [('draft', 'DRAFT'), ('confirm', 'CONFIRM'), ('borrowed', 'BORROWED'), ('returned', 'RETURNED'), ],
        default='draft', string='Status')
    book_id = fields.Many2one(comodel_name='library.book.detail', string='Book', required=True, )
    author = fields.Char(string='Author', related='book_id.author', )
    person_id = fields.Many2one(comodel_name='librarian.detail', string='Librarian', required=True, )
    student_id = fields.Many2one(comodel_name='student.detail', string="Student", required=True, )
    issue_date = fields.Date(string='Issue_Date', )
    return_date = fields.Date(string='Return Date')
    student_id = fields.Many2one(comodel_name='student.detail', string="Student", required=True)
    chatter = fields.Text(string='Chatter', track_visibility='onchange', track_sequence=5)

    def set_confirm(self):
        self.ensure_one()
        self.write({'status': 'confirm'})

    def set_borrowed(self):
        new_status = 'borrowed' if self.status == 'draft' else 'draft'
        self.write({'status': 'borrowed'})
        for book in self:
            book.write({'issue_date': fields.Date.today()})

    def set_returned(self):
        self.write({'status': 'returned'})
        for book in self:
            book.write({'return_date': fields.Date.today()})

    def print_transaction_details(self):
        return self.env.ref('lms.action_report_transaction_details').report_action(self)

